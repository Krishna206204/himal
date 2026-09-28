from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from .models import Appointment
from .forms import AppointmentForm, get_available_slots
from account.models import User


@login_required
def appointment_list(request):
    user = request.user
    role_str = str(user.role).upper() if user.role else ""

    if role_str == User.ADMIN or user.is_superuser or user.is_staff:
        appointments = Appointment.objects.all().order_by('-appointment_date')
    elif role_str == User.VETERINARIAN:
        appointments = Appointment.objects.filter(veterinarian=user).order_by('-appointment_date')
    else:
        # Pet Owner
        appointments = Appointment.objects.filter(pet_owner=user).order_by('-appointment_date')

    status = request.GET.get("status", "")
    if status in dict(Appointment.STATUS_CHOICES):
        appointments = appointments.filter(status=status)
    day = parse_date(request.GET.get("date", ""))
    if day:
        appointments = appointments.filter(appointment_date__date=day)
    if day is None and request.GET.get("date"):
        messages.error(request, "Enter a valid date to filter appointments.")

    return render(request, 'appointment/appointment_list.html', {
        'appointments': appointments.select_related(
            "animal", "pet_owner", "veterinarian"
        ),
        'status_choices': Appointment.STATUS_CHOICES,
        'selected_status': status,
        'selected_date': day,
    })


@login_required
def create_appointment(request):
    if request.user.role != User.PET_OWNER:
        raise PermissionDenied
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                if form.cleaned_data["time_slot"] not in {
                    slot.strftime("%H:%M")
                    for slot in get_available_slots(
                        form.cleaned_data["date"],
                        form.cleaned_data["veterinarian"],
                        form.cleaned_data["animal"],
                    )
                }:
                    form.add_error(
                        "time_slot",
                        "That time was just booked. Please choose another available slot.",
                    )
                    return render(
                        request,
                        "appointment/appointment_form.html",
                        {"form": form},
                        status=409,
                    )
                appointment = form.save(commit=False)
                appointment.pet_owner = request.user
                appointment.save()
            messages.success(request, "Appointment requested successfully!")
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'appointment/appointment_form.html', {'form': form})


@login_required
def available_slots(request):
    if request.user.role != User.PET_OWNER:
        raise PermissionDenied
    day = parse_date(request.GET.get("date", ""))
    veterinarian = User.objects.filter(
        role=User.VETERINARIAN,
        is_active=True,
        pk=request.GET.get("veterinarian"),
    ).first()
    animal = request.user.animals.filter(
        pk=request.GET.get("animal")
    ).first()
    if day is None or veterinarian is None or animal is None:
        return JsonResponse(
            {"error": "Choose a valid date, veterinarian, and one of your pets."},
            status=400,
        )
    slots = get_available_slots(day, veterinarian, animal)
    return JsonResponse({
        "slots": [
            {"value": slot.strftime("%H:%M"), "label": slot.strftime("%I:%M %p").lstrip("0")}
            for slot in slots
        ],
    })


@login_required
@require_POST
def update_appointment_status(request, pk, status):
    appointment = get_object_or_404(
        Appointment.objects.select_related("veterinarian", "pet_owner"),
        pk=pk,
    )
    allowed_statuses = dict(Appointment.STATUS_CHOICES)
    if status not in allowed_statuses:
        raise PermissionDenied

    is_admin = request.user.is_staff or request.user.is_superuser or request.user.role == User.ADMIN
    is_assigned_vet = (
        request.user == appointment.veterinarian
        and request.user.role == User.VETERINARIAN
    )
    is_owner_cancelling = (
        request.user == appointment.pet_owner
        and appointment.status == "PENDING"
        and status == "CANCELLED"
    )
    if not (is_admin or is_assigned_vet or is_owner_cancelling):
        raise PermissionDenied

    transitions = {
        "PENDING": {"CONFIRMED", "CANCELLED"},
        "CONFIRMED": {"COMPLETED", "CANCELLED"},
        "COMPLETED": set(),
        "CANCELLED": set(),
    }
    if status not in transitions[appointment.status]:
        messages.error(request, "That appointment status change is not allowed.")
        return redirect("appointment_list")

    appointment.status = status
    appointment.save(update_fields=["status"])
    messages.success(
        request,
        f"Appointment status changed to {allowed_statuses[status]}.",
    )

    return redirect('appointment_list')
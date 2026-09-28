from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from .models import Appointment
from .forms import AppointmentForm
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

    return render(request, 'appointment/appointment_list.html', {'appointments': appointments})


@login_required
def create_appointment(request):
    if request.user.role != User.PET_OWNER:
        raise PermissionDenied
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.pet_owner = request.user
            appointment.save()
            messages.success(request, "Appointment requested successfully!")
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'appointment/appointment_form.html', {'form': form})


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
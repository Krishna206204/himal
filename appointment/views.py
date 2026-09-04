from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
def update_appointment_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk)

    # Restrict status changes to assigned Vet or Admin
    if request.user == appointment.veterinarian or request.user.is_superuser:
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment status changed to {status}.")
    else:
        messages.error(request, "You are not authorized to update this appointment.")

    return redirect('appointment_list')
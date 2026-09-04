from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm


@login_required
def appointment_list(request):
    """Filter appointments based on user roles."""
    if request.user.role == request.user.PET_OWNER:
        appointments = Appointment.objects.filter(animal__owner__user=request.user)
    elif request.user.role == request.user.VETERINARIAN:
        appointments = Appointment.objects.filter(veterinarian=request.user)
    else:
        appointments = Appointment.objects.all()

    return render(request, "base.html", {"appointments": appointments})


@login_required
def book_appointment(request):
    """Handle booking an appointment."""
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f"Appointment booked for {appointment.animal.name}!")
            return redirect("appointment_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm()

    return render(request, "base.html", {"form": form})


@login_required
def update_appointment_status(request, pk, status):
    """Allow Vets/Admins to quickly update appointment status."""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user.role in [request.user.VETERINARIAN, request.user.ADMIN]:
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment status changed to {status}.")
    return redirect("appointment_list")
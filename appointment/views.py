from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Appointment
from animal.models import Animal
from account.models import User


@login_required
def owner_appointment_list(request):
    """
    Show appointments belonging to the logged-in pet owner.
    """

    if request.user.role != User.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to view appointments."
        )
        return redirect("dashboard")

    appointments = (
        Appointment.objects
        .filter(animal__owner=request.user)
        .select_related("animal", "veterinarian")
        .order_by(
            "-appointment_date",
            "-appointment_time"
        )
    )

    context = {
        "appointments": appointments,
    }

    return render(
        request,
        "appointment/owner_appointments.html",
        context
    )


@login_required
def book_appointment(request):
    """
    Allow a pet owner to book an appointment
    for one of their own pets.
    """

    if request.user.role != User.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to book an appointment."
        )
        return redirect("dashboard")

    # Only show pets belonging to this owner
    animals = Animal.objects.filter(
        owner=request.user
    ).order_by("name")

    # Only show veterinarians
    veterinarians = User.objects.filter(
        role=User.VETERINARIAN
    ).order_by("first_name", "last_name", "username")

    if request.method == "POST":

        animal_id = request.POST.get("animal")
        veterinarian_id = request.POST.get("veterinarian")
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        reason = request.POST.get("reason", "").strip()

        # Required fields
        if not animal_id:
            messages.error(
                request,
                "Please select your pet."
            )

            return render(
                request,
                "appointment/book_appointment.html",
                {
                    "animals": animals,
                    "veterinarians": veterinarians,
                }
            )

        if not appointment_date:
            messages.error(
                request,
                "Please select an appointment date."
            )

            return render(
                request,
                "appointment/book_appointment.html",
                {
                    "animals": animals,
                    "veterinarians": veterinarians,
                }
            )

        if not appointment_time:
            messages.error(
                request,
                "Please select an appointment time."
            )

            return render(
                request,
                "appointment/book_appointment.html",
                {
                    "animals": animals,
                    "veterinarians": veterinarians,
                }
            )

        if not reason:
            messages.error(
                request,
                "Please enter the reason for the appointment."
            )

            return render(
                request,
                "appointment/book_appointment.html",
                {
                    "animals": animals,
                    "veterinarians": veterinarians,
                }
            )

        # IMPORTANT:
        # Get the animal using owner=request.user.
        # This prevents a pet owner from booking
        # an appointment for another owner's pet.
        animal = get_object_or_404(
            Animal,
            id=animal_id,
            owner=request.user
        )

        # Veterinarian is optional because your model
        # allows veterinarian=null.
        veterinarian = None

        if veterinarian_id:
            veterinarian = get_object_or_404(
                User,
                id=veterinarian_id,
                role=User.VETERINARIAN
            )

        Appointment.objects.create(
            animal=animal,
            veterinarian=veterinarian,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            status="PENDING"
        )

        messages.success(
            request,
            "Appointment booked successfully. It is currently pending confirmation."
        )

        return redirect("owner-appointments")

    context = {
        "animals": animals,
        "veterinarians": veterinarians,
    }

    return render(
        request,
        "appointment/book_appointment.html",
        context
    )
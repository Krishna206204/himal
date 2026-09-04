from django.db import models
from account.models import User
from animal.models import Animal  # Updated import


class Appointment(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    animal = models.ForeignKey(
        Animal,  # Updated model reference
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    veterinarian = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vet_appointments",
        limit_choices_to={"role": User.VETERINARIAN}
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.animal} - {self.appointment_date} {self.appointment_time}"
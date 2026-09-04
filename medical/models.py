from django.db import models
from animal.models import Animal
from account.models import VeterinarianProfile


class MedicalRecord(models.Model):

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="medical_records"
    )

    veterinarian = models.ForeignKey(
        VeterinarianProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medical_records"
    )

    appointment = models.ForeignKey(
        "appointment.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records"
    )

    diagnosis = models.TextField()

    symptoms = models.TextField(
        blank=True,
        null=True
    )

    treatment = models.TextField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    record_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.animal} - {self.diagnosis} ({self.record_date})"

    class Meta:
        ordering = ["-record_date"]
        verbose_name = "Medical Record"
        verbose_name_plural = "Medical Records"


class Prescription(models.Model):

    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )

    medicine_name = models.CharField(
        max_length=200
    )

    dosage = models.CharField(
        max_length=100
    )

    frequency = models.CharField(
        max_length=100
    )

    duration = models.CharField(
        max_length=100
    )

    instructions = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.medicine_name} - {self.medical_record.animal}"
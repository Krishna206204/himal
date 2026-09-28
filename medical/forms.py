from django import forms
from .models import MedicalRecord, Prescription
from account.models import User
from animal.models import Animal
from appointment.models import Appointment


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            "animal",
            "appointment",
            "diagnosis",
            "symptoms",
            "treatment",
            "notes",
            "record_date",
        ]
        widgets = {
            "record_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "diagnosis": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "symptoms": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "treatment": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animal"].queryset = Animal.objects.order_by("name")
        self.fields["appointment"].queryset = Appointment.objects.none()
        if user.role == User.VETERINARIAN:
            self.fields["animal"].queryset = Animal.objects.filter(
                appointments__veterinarian=user
            ).distinct().order_by("name")
            self.fields["appointment"].queryset = Appointment.objects.filter(
                veterinarian=user,
                status__in=["CONFIRMED", "COMPLETED"],
            ).order_by("-appointment_date")
        elif user.is_staff or user.is_superuser or user.role == User.ADMIN:
            self.fields["veterinarian"] = forms.ModelChoiceField(
                queryset=User.objects.filter(
                    role=User.VETERINARIAN,
                    is_active=True,
                ).order_by("username"),
                widget=forms.Select(attrs={"class": "form-control"}),
            )
            self.fields["appointment"].queryset = Appointment.objects.order_by(
                "-appointment_date"
            )


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["medicine_name", "dosage", "frequency", "duration", "instructions"]
        widgets = {
            "medicine_name": forms.TextInput(attrs={"class": "form-control"}),
            "dosage": forms.TextInput(attrs={"class": "form-control"}),
            "frequency": forms.TextInput(attrs={"class": "form-control"}),
            "duration": forms.TextInput(attrs={"class": "form-control"}),
            "instructions": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }
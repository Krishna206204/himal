from django import forms
from .models import MedicalRecord, Prescription


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            "animal",
            "veterinarian",
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


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["medicine_name", "dosage", "frequency", "duration", "instructions"]
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }
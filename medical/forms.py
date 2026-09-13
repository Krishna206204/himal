# medical/forms.py

from django import forms
from .models import MedicalRecord
from appointment.models import Appointment


class MedicalRecordForm(forms.ModelForm):

    appointment = forms.ModelChoiceField(
        queryset=Appointment.objects.none()
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "appointment",
            "diagnosis",
            "symptoms",
            "treatment",
            "notes",
            "record_date",
        ]

    def __init__(self, *args, veterinarian=None, **kwargs):
        super().__init__(*args, **kwargs)

        if veterinarian:
            self.fields["appointment"].queryset = (
                Appointment.objects.filter(
                    veterinarian=veterinarian
                )
                .select_related("animal")
                .order_by("-appointment_date")
            )
# medical/forms.py

from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import MedicalRecord, Prescription
from appointment.models import Appointment


class MedicalRecordForm(forms.ModelForm):

    appointment = forms.ModelChoiceField(
        queryset=Appointment.objects.none(),
        empty_label="Choose Appointment"
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "appointment",
            "record_date",
            "symptoms",
            "diagnosis",
            "treatment",
            "notes",
        ]

        widgets = {
            "record_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "max": timezone.now().date().isoformat(),
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500 "
                        "focus:ring-2 focus:ring-emerald-200"
                    ),
                }
            ),
            "symptoms": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    ),
                }
            ),
            "diagnosis": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    ),
                }
            ),
            "treatment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    ),
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    ),
                }
            ),
        }

    def __init__(self, *args, veterinarian=None, **kwargs):
        super().__init__(*args, **kwargs)

        if veterinarian:
            self.fields["appointment"].queryset = (
                Appointment.objects.filter(
                    veterinarian=veterinarian,
                    status="CONFIRMED"
                )
                .select_related("animal")
                .order_by("-appointment_date")
            )

    def clean_record_date(self):
        record_date = self.cleaned_data.get("record_date")

        if record_date and record_date > timezone.now().date():
            raise forms.ValidationError(
                "Medical record date cannot be in the future."
            )

        return record_date


class PrescriptionForm(forms.ModelForm):

    class Meta:
        model = Prescription

        fields = [
            "medicine_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
        ]

        widgets = {
            "medicine_name": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    )
                }
            ),
            "dosage": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    )
                }
            ),
            "frequency": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    )
                }
            ),
            "duration": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    )
                }
            ),
            "instructions": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": (
                        "w-full rounded-lg border-2 border-slate-300 "
                        "px-3 py-2 focus:border-emerald-500"
                    )
                }
            ),
        }


PrescriptionFormSet = inlineformset_factory(
    MedicalRecord,
    Prescription,
    form=PrescriptionForm,
    extra=1,
    can_delete=True
)
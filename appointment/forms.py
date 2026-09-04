from django import forms
from .models import Appointment
from account.models import User


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["animal", "veterinarian", "appointment_date", "appointment_time", "reason", "notes"]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "reason": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict veterinarian choices to Veterinarians only
        self.fields["veterinarian"].queryset = User.objects.filter(role=User.VETERINARIAN)
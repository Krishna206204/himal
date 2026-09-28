from django import forms
from django.utils import timezone
from django.db.models import Q
from .models import Appointment
from account.models import User
from animal.models import Animal


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # STRICTLY match fields present in Appointment models.py
        fields = ['veterinarian', 'animal', 'appointment_date', 'reason']
        widgets = {
            'appointment_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                }
            ),
            'reason': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'form-control',
                    'placeholder': 'Describe the reason for the visit...',
                }
            ),
            'veterinarian': forms.Select(attrs={'class': 'form-control'}),
            'animal': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['veterinarian'].queryset = User.objects.filter(
            role=User.VETERINARIAN,
            is_active=True,
        ).order_by('first_name', 'username')

        self.fields['animal'].queryset = Animal.objects.none()
        if user:
            self.fields['animal'].queryset = Animal.objects.filter(
                owner=user
            ).order_by('name')

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]
        if appointment_date <= timezone.now():
            raise forms.ValidationError("Choose a future date and time.")
        return appointment_date

    def clean(self):
        cleaned = super().clean()
        veterinarian = cleaned.get("veterinarian")
        animal = cleaned.get("animal")
        appointment_date = cleaned.get("appointment_date")
        if veterinarian and animal and appointment_date:
            conflicts = Appointment.objects.filter(
                appointment_date=appointment_date,
                status__in=("PENDING", "CONFIRMED"),
            ).filter(Q(veterinarian=veterinarian) | Q(animal=animal))
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise forms.ValidationError(
                    "This veterinarian or pet already has an appointment at that time."
                )
        return cleaned
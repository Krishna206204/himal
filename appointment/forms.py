from django import forms
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

        # Filter veterinarians dynamically
        if hasattr(User, 'VETERINARIAN'):
            self.fields['veterinarian'].queryset = User.objects.filter(
                role=User.VETERINARIAN
            )

        # Filter animals to show only those belonging to the logged-in owner
        if user and hasattr(Animal, 'owner'):
            self.fields['animal'].queryset = Animal.objects.filter(owner=user)
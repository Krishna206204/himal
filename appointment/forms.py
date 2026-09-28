from datetime import datetime, time, timedelta

from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from account.models import User
from animal.models import Animal
from .models import Appointment


def appointment_slot_starts(day):
    opens_at = time.fromisoformat(settings.APPOINTMENT_OPEN_TIME)
    closes_at = time.fromisoformat(settings.APPOINTMENT_CLOSE_TIME)
    slot_minutes = settings.APPOINTMENT_SLOT_MINUTES
    if slot_minutes <= 0:
        return []

    opening_minutes = opens_at.hour * 60 + opens_at.minute
    closing_minutes = closes_at.hour * 60 + closes_at.minute
    return [
        time(hour=minute // 60, minute=minute % 60)
        for minute in range(opening_minutes, closing_minutes, slot_minutes)
        if minute + slot_minutes <= closing_minutes
    ]


def get_available_slots(day, veterinarian, animal=None):
    if not day or not veterinarian:
        return []

    now = timezone.now()
    duration = timedelta(minutes=settings.APPOINTMENT_SLOT_MINUTES)
    available = []
    for slot_time in appointment_slot_starts(day):
        starts_at = timezone.make_aware(
            datetime.combine(day, slot_time),
            timezone.get_current_timezone(),
        )
        if starts_at <= now:
            continue
        conflicts = Appointment.objects.filter(
            appointment_date__gt=starts_at - duration,
            appointment_date__lt=starts_at + duration,
            status__in=("PENDING", "CONFIRMED"),
        )
        conflicts = conflicts.filter(
            Q(veterinarian=veterinarian)
            | (Q(animal=animal) if animal is not None else Q(pk__in=[]))
        )
        if not conflicts.exists():
            available.append(slot_time)
    return available


class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        label="Appointment date",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    time_slot = forms.ChoiceField(
        label="Available appointment time",
        choices=(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Appointment
        fields = ("veterinarian", "animal", "reason")
        widgets = {
            "reason": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Describe the reason for the visit...",
            }),
            "veterinarian": forms.Select(attrs={"class": "form-control"}),
            "animal": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["veterinarian"].queryset = User.objects.filter(
            role=User.VETERINARIAN,
            is_active=True,
        ).order_by("first_name", "username")
        self.fields["animal"].queryset = Animal.objects.none()
        if self.user:
            self.fields["animal"].queryset = Animal.objects.filter(
                owner=self.user
            ).order_by("name")

        self.fields["time_slot"].choices = [
            ("", "Select a date and veterinarian first")
        ]
        raw_date = self.data.get("date") if self.is_bound else self.initial.get("date")
        if raw_date:
            try:
                selected_date = forms.DateField().clean(raw_date)
            except forms.ValidationError:
                selected_date = None
            slots = appointment_slot_starts(selected_date)
            self.fields["time_slot"].choices = [
                ("", "Choose an available time")
            ] + [
                (slot.strftime("%H:%M"), slot.strftime("%I:%M %p").lstrip("0"))
                for slot in slots
            ]

    def clean(self):
        cleaned = super().clean()
        day = cleaned.get("date")
        slot_value = cleaned.get("time_slot")
        veterinarian = cleaned.get("veterinarian")
        animal = cleaned.get("animal")
        if day and slot_value and veterinarian and animal:
            slot_time = time.fromisoformat(slot_value)
            starts_at = timezone.make_aware(
                datetime.combine(day, slot_time),
                timezone.get_current_timezone(),
            )
            if starts_at <= timezone.now():
                self.add_error("date", "Choose a future appointment date and time.")
            elif slot_time not in get_available_slots(day, veterinarian, animal):
                self.add_error(
                    "time_slot",
                    "This veterinarian or pet already has an appointment during that slot. Choose another time.",
                )
            else:
                cleaned["appointment_date"] = starts_at
        return cleaned

    def save(self, commit=True):
        self.instance.appointment_date = self.cleaned_data["appointment_date"]
        return super().save(commit=commit)

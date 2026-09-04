from django.contrib import admin
from .models import Appointment
from account.models import User


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "animal",
        "veterinarian",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "appointment_date",
        "veterinarian",
    )

    search_fields = (
        "animal__name",
        "veterinarian__username",
        "veterinarian__first_name",
        "reason",
    )

    ordering = ("-appointment_date", "-appointment_time")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restrict veterinarian choices in Admin panel to Users with VETERINARIAN role."""
        if db_field.name == "veterinarian":
            kwargs["queryset"] = User.objects.filter(role=User.VETERINARIAN)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
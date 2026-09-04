from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Only list fields that exist on the Appointment model
    list_display = ('id', 'pet_owner', 'veterinarian', 'animal', 'appointment_date', 'status', 'created_at')
    list_filter = ('status', 'appointment_date')
    search_fields = ('pet_owner__username', 'veterinarian__username', 'animal__name', 'reason')
    ordering = ('-appointment_date',)
from django.conf import settings


def clinic_settings(request):
    return {
        "APPOINTMENT_SLOT_MINUTES": settings.APPOINTMENT_SLOT_MINUTES,
        "APPOINTMENT_OPEN_TIME": settings.APPOINTMENT_OPEN_TIME,
        "APPOINTMENT_CLOSE_TIME": settings.APPOINTMENT_CLOSE_TIME,
    }

from django.contrib import admin
from .models import MedicalRecord, Prescription


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "animal",
        "veterinarian",
        "diagnosis",
        "record_date",
        "created_at",
    )
    list_filter = (
        "record_date",
        "veterinarian",
    )
    search_fields = (
        "animal__name",
        "diagnosis",
        "symptoms",
        "veterinarian__user__username",
    )
    inlines = [PrescriptionInline]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "medicine_name",
        "medical_record",
        "dosage",
        "frequency",
        "duration",
    )
    search_fields = (
        "medicine_name",
        "medical_record__animal__name",
    )
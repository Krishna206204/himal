from django.contrib import admin

# Register your models here.
from .models import MedicalRecord,Prescription

admin.site.register(MedicalRecord),
admin.site.register(Prescription)
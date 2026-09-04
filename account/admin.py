from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User,VeterinarianProfile,  PetOwnerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "phone",
        "is_active",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    ordering = (
        "username",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "address",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "address",
                )
            },
        ),
    )


@admin.register(VeterinarianProfile)
class VeterinarianProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "license_number",
        "specialization",
        "qualification",
        "experience_years",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "license_number",
        "specialization",
    )

    list_filter = (
        "specialization",
        "joined_date",
    )


@admin.register(PetOwnerProfile)
class PetOwnerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "emergency_contact_phone",
    )

    search_fields = (
        "user__username",
        "user__first_name",
    )

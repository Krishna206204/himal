from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VeterinarianProfile, PetOwnerProfile


# -----------------------------------------------------------------------------
# Profile Inlines (Allows editing profiles directly inside the User edit page)
# -----------------------------------------------------------------------------
class VeterinarianProfileInline(admin.StackedInline):
    model = VeterinarianProfile
    can_delete = False
    verbose_name_plural = "Veterinarian Profile"
    fk_name = "user"


class PetOwnerProfileInline(admin.StackedInline):
    model = PetOwnerProfile
    can_delete = False
    verbose_name_plural = "Pet Owner Profile"
    fk_name = "user"


# -----------------------------------------------------------------------------
# Custom User Admin
# -----------------------------------------------------------------------------
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

    def get_inlines(self, request, obj=None):
        """Dynamically displays the matching profile inline based on user role."""
        if obj:
            if obj.role == User.VETERINARIAN:
                return [VeterinarianProfileInline]
            elif obj.role == User.PET_OWNER:
                return [PetOwnerProfileInline]
        return []


# -----------------------------------------------------------------------------
# Veterinarian Profile Admin
# -----------------------------------------------------------------------------
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter user selection dropdown to only show users with VETERINARIAN role."""
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(role=User.VETERINARIAN)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# -----------------------------------------------------------------------------
# Pet Owner Profile Admin
# -----------------------------------------------------------------------------
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter user selection dropdown to only show users with PET_OWNER role."""
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(role=User.PET_OWNER)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
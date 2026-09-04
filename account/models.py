from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ADMIN = "ADMIN"
    VETERINARIAN = "VETERINARIAN"
    PET_OWNER = "PET_OWNER"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (VETERINARIAN, "Veterinarian"),
        (PET_OWNER, "Pet Owner"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=PET_OWNER
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"



class VeterinarianProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="veterinarian_profile",
        limit_choices_to={"role": User.VETERINARIAN}
    )

    license_number = models.CharField(
        max_length=100,
        unique=True
    )

    specialization = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    qualification = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    experience_years = models.PositiveIntegerField(
        default=0
    )

    joined_date = models.DateField(
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f"Dr. {self.user.get_full_name()}"
            if self.user.get_full_name()
            else self.user.username
        )



class PetOwnerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pet_owner_profile",
        limit_choices_to={"role": User.PET_OWNER}
    )


    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            self.user.get_full_name()
            if self.user.get_full_name()
            else self.user.username
        )

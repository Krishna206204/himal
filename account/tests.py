from django.test import TestCase
from django.urls import reverse

from .models import PetOwnerProfile, User, VeterinarianProfile


class RegistrationTests(TestCase):
    def test_registering_owner_creates_profile_and_hashes_password(self):
        response = self.client.post(reverse("register"), {
            "username": "new-owner",
            "first_name": "Sam",
            "last_name": "Peterson",
            "email": "sam@example.com",
            "role": User.PET_OWNER,
            "password": "Strong!Password73",
            "confirm_password": "Strong!Password73",
        })

        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="new-owner")
        self.assertTrue(user.check_password("Strong!Password73"))
        self.assertTrue(PetOwnerProfile.objects.filter(user=user).exists())

    def test_public_registration_cannot_create_admin(self):
        response = self.client.post(reverse("register"), {
            "username": "bad-admin",
            "email": "admin@example.com",
            "role": User.ADMIN,
            "password": "Strong!Password73",
            "confirm_password": "Strong!Password73",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="bad-admin").exists())

    def test_registering_veterinarian_requires_license_and_creates_profile(self):
        response = self.client.post(reverse("register"), {
            "username": "dr-lee",
            "email": "lee@example.com",
            "role": User.VETERINARIAN,
            "license_number": "LICENSE-LEE-1",
            "specialization": "Feline medicine",
            "qualification": "DVM",
            "password": "Strong!Password73",
            "confirm_password": "Strong!Password73",
        })

        self.assertRedirects(response, reverse("login"))
        veterinarian = User.objects.get(username="dr-lee")
        self.assertTrue(
            VeterinarianProfile.objects.filter(
                user=veterinarian,
                license_number="LICENSE-LEE-1",
            ).exists()
        )

    def test_logout_requires_post(self):
        user = User.objects.create_user(username="owner", password="Strong!Password73")
        self.client.force_login(user)

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse("forgot_password"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reset your password")

    def test_owner_dashboard_renders(self):
        user = User.objects.create_user(
            username="dashboard-owner",
            password="Strong!Password73",
            role=User.PET_OWNER,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your pets")

    def test_veterinarian_dashboard_renders(self):
        veterinarian = User.objects.create_user(
            username="dashboard-vet",
            password="Strong!Password73",
            role=User.VETERINARIAN,
        )
        VeterinarianProfile.objects.create(
            user=veterinarian,
            license_number="DASH-VET-001",
        )
        self.client.force_login(veterinarian)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your clinic")

    def test_admin_dashboard_renders(self):
        administrator = User.objects.create_user(
            username="dashboard-admin",
            password="Strong!Password73",
            role=User.ADMIN,
        )
        self.client.force_login(administrator)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clinic overview")

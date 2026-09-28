import re

from django.test import TestCase
from django.core import mail
from django.urls import reverse
from django.test import override_settings

from .models import PetOwnerProfile, User, VeterinarianProfile


class RegistrationTests(TestCase):
    def test_public_home_page_has_login_and_registration_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Here for every")
        self.assertContains(response, ".public-nav { position: sticky; top: 0;")
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("register"))

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
        self.assertContains(response, "Forgot your password?")
        self.assertContains(response, "Secure account recovery")
        self.assertContains(response, ".auth-layout")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_flow_sends_link_and_updates_password(self):
        user = User.objects.create_user(
            username="reset-owner",
            email="reset@example.com",
            password="Old!Password472",
        )
        response = self.client.post(reverse("forgot_password"), {
            "email": "reset@example.com",
        })

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        reset_link = re.search(
            r"http://testserver(/reset/[^\s]+)",
            mail.outbox[0].body,
        )
        self.assertIsNotNone(reset_link)
        response = self.client.get(reset_link.group(1), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose a new password")
        reset_form_url = response.request["PATH_INFO"]

        response = self.client.post(reset_form_url, {
            "new_password1": "Fresh!Password882",
            "new_password2": "Fresh!Password882",
        })

        self.assertRedirects(response, reverse("password_reset_complete"))
        user.refresh_from_db()
        self.assertTrue(user.check_password("Fresh!Password882"))
        response = self.client.get(reverse("password_reset_complete"))
        self.assertContains(response, "Your password is updated")

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
        self.assertContains(response, "Doctor dashboard")

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

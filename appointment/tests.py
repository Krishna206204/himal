from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import User, VeterinarianProfile
from animal.models import Animal
from .models import Appointment


class AppointmentWorkflowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="Strong!Password73", role=User.PET_OWNER
        )
        self.other_owner = User.objects.create_user(
            username="other", password="Strong!Password73", role=User.PET_OWNER
        )
        self.vet = User.objects.create_user(
            username="vet", password="Strong!Password73", role=User.VETERINARIAN
        )
        VeterinarianProfile.objects.create(user=self.vet, license_number="VET-001")
        self.pet = Animal.objects.create(name="Milo", species="Cat", owner=self.owner)
        self.other_pet = Animal.objects.create(
            name="Bella", species="Dog", owner=self.other_owner
        )
        self.appointment = Appointment.objects.create(
            pet_owner=self.owner,
            veterinarian=self.vet,
            animal=self.pet,
            appointment_date=timezone.now() + timedelta(days=2),
            reason="Annual checkup",
        )

    def test_owner_only_sees_their_appointments(self):
        Appointment.objects.create(
            pet_owner=self.other_owner,
            veterinarian=self.vet,
            animal=self.other_pet,
            appointment_date=timezone.now() + timedelta(days=3),
            reason="Vaccination",
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("appointment_list"))

        self.assertContains(response, "Milo")
        self.assertNotContains(response, "Bella")

    def test_owner_cannot_book_another_owners_pet(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("create_appointment"), {
            "veterinarian": self.vet.pk,
            "animal": self.other_pet.pk,
            "appointment_date": (timezone.now() + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M"),
            "reason": "Checkup",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_owner_cannot_book_in_the_past(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("create_appointment"), {
            "veterinarian": self.vet.pk,
            "animal": self.pet.pk,
            "appointment_date": (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "reason": "Checkup",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose a future date and time.")
        self.assertEqual(Appointment.objects.count(), 1)

    def test_duplicate_slot_is_rejected(self):
        slot = timezone.make_aware(datetime(2030, 1, 10, 10, 0))
        Appointment.objects.filter(pk=self.appointment.pk).update(
            appointment_date=slot
        )
        self.client.force_login(self.owner)

        response = self.client.post(reverse("create_appointment"), {
            "veterinarian": self.vet.pk,
            "animal": self.pet.pk,
            "appointment_date": slot.strftime("%Y-%m-%dT%H:%M"),
            "reason": "Checkup",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already has an appointment at that time")
        self.assertEqual(Appointment.objects.count(), 1)

    def test_status_change_is_post_only_and_vet_can_confirm(self):
        self.client.force_login(self.vet)
        url = reverse(
            "update_appointment_status",
            args=[self.appointment.pk, "CONFIRMED"],
        )

        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)

        self.assertRedirects(response, reverse("appointment_list"))
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "CONFIRMED")

    def test_owner_cannot_confirm_their_appointment(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse(
            "update_appointment_status",
            args=[self.appointment.pk, "CONFIRMED"],
        ))

        self.assertEqual(response.status_code, 403)

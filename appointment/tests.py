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

    def booking_data(self, *, day=None, slot="10:00", animal=None):
        day = day or (timezone.localdate() + timedelta(days=1))
        return {
            "veterinarian": self.vet.pk,
            "animal": (animal or self.pet).pk,
            "date": day.isoformat(),
            "time_slot": slot,
            "reason": "Checkup",
        }

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

        response = self.client.post(
            reverse("create_appointment"),
            self.booking_data(animal=self.other_pet),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_owner_cannot_book_in_the_past(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("create_appointment"),
            self.booking_data(day=timezone.localdate() - timedelta(days=1)),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose a future appointment date and time.")
        self.assertEqual(Appointment.objects.count(), 1)

    def test_duplicate_slot_is_rejected(self):
        slot = timezone.make_aware(datetime(2030, 1, 10, 10, 0))
        Appointment.objects.filter(pk=self.appointment.pk).update(
            appointment_date=slot
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("create_appointment"),
            self.booking_data(day=slot.date(), slot="10:00"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already has an appointment during that slot")
        self.assertEqual(Appointment.objects.count(), 1)

    def test_owner_can_book_an_open_slot(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("create_appointment"),
            self.booking_data(),
        )

        self.assertRedirects(response, reverse("appointment_list"))
        booking = Appointment.objects.get(pet_owner=self.owner, pk__gt=self.appointment.pk)
        self.assertEqual(timezone.localtime(booking.appointment_date).hour, 10)
        self.assertEqual(booking.status, "PENDING")

    def test_available_slot_endpoint_only_returns_open_slots(self):
        slot = timezone.make_aware(datetime.combine(
            timezone.localdate() + timedelta(days=3),
            datetime.strptime("10:00", "%H:%M").time(),
        ))
        Appointment.objects.create(
            pet_owner=self.other_owner,
            veterinarian=self.vet,
            animal=self.other_pet,
            appointment_date=slot,
            reason="Booked already",
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("available_appointment_slots"), {
            "date": slot.date().isoformat(),
            "veterinarian": self.vet.pk,
            "animal": self.pet.pk,
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("10:00", [item["value"] for item in response.json()["slots"]])
        self.assertIn("10:30", [item["value"] for item in response.json()["slots"]])

    def test_booking_requires_configured_slot_time(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("create_appointment"),
            self.booking_data(slot="10:15"),
        )

        self.assertEqual(response.status_code, 200)
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

    def test_appointment_filters_apply_status_and_date(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("appointment_list"), {
            "status": "PENDING",
            "date": self.appointment.appointment_date.date().isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annual checkup")
        response = self.client.get(reverse("appointment_list"), {
            "status": "CANCELLED",
            "date": self.appointment.appointment_date.date().isoformat(),
        })
        self.assertNotContains(response, "Annual checkup")

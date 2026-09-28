from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import User, VeterinarianProfile
from animal.models import Animal
from appointment.models import Appointment
from .models import MedicalRecord, Prescription


class MedicalRecordAccessTests(TestCase):
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
        self.profile = VeterinarianProfile.objects.create(
            user=self.vet, license_number="VET-MED-001"
        )
        self.pet = Animal.objects.create(name="Milo", species="Cat", owner=self.owner)
        self.other_pet = Animal.objects.create(
            name="Bella", species="Dog", owner=self.other_owner
        )
        self.appointment = Appointment.objects.create(
            pet_owner=self.owner,
            veterinarian=self.vet,
            animal=self.pet,
            appointment_date=timezone.now() + timedelta(days=1),
            reason="Checkup",
            status="CONFIRMED",
        )
        self.record = MedicalRecord.objects.create(
            animal=self.pet,
            veterinarian=self.profile,
            appointment=self.appointment,
            diagnosis="Healthy",
            record_date=date.today(),
        )

    def test_owner_can_view_their_record_but_not_other_pets(self):
        other_record = MedicalRecord.objects.create(
            animal=self.other_pet,
            veterinarian=self.profile,
            diagnosis="Other patient",
            record_date=date.today(),
        )
        self.client.force_login(self.owner)

        self.assertEqual(
            self.client.get(reverse("medical_record_detail", args=[self.record.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("medical_record_detail", args=[other_record.pk])).status_code,
            404,
        )

    def test_vet_can_create_record_and_prescription(self):
        self.client.force_login(self.vet)
        create_response = self.client.post(reverse("add_medical_record"), {
            "animal": self.pet.pk,
            "appointment": self.appointment.pk,
            "diagnosis": "Minor irritation",
            "symptoms": "Itching",
            "treatment": "Topical care",
            "notes": "",
            "record_date": date.today().isoformat(),
        })

        self.assertRedirects(create_response, reverse(
            "medical_record_detail",
            args=[MedicalRecord.objects.get(diagnosis="Minor irritation").pk],
        ))
        created_record = MedicalRecord.objects.get(diagnosis="Minor irritation")
        prescription_response = self.client.post(
            reverse("add_prescription", args=[created_record.pk]),
            {
                "medicine_name": "Cream",
                "dosage": "Apply thin layer",
                "frequency": "Twice daily",
                "duration": "5 days",
                "instructions": "Stop if irritation worsens",
            },
        )

        self.assertRedirects(
            prescription_response,
            reverse("medical_record_detail", args=[created_record.pk]),
        )
        self.assertTrue(Prescription.objects.filter(medical_record=created_record).exists())

    def test_owner_cannot_create_medical_record(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("add_medical_record"))

        self.assertEqual(response.status_code, 403)

from django.test import TestCase
from django.urls import reverse

from account.models import User
from .models import Animal


class AnimalAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", password="Strong!Password73", role=User.PET_OWNER
        )
        self.other_owner = User.objects.create_user(
            username="other", password="Strong!Password73", role=User.PET_OWNER
        )
        self.pet = Animal.objects.create(
            name="Milo", species="Cat", owner=self.owner
        )
        self.other_pet = Animal.objects.create(
            name="Bella", species="Dog", owner=self.other_owner
        )

    def test_owner_only_sees_their_animals(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("pet_list"))

        self.assertContains(response, "Milo")
        self.assertNotContains(response, "Bella")

    def test_owner_cannot_view_another_owners_pet(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("pet_detail", args=[self.other_pet.pk]))

        self.assertEqual(response.status_code, 403)

    def test_owner_can_add_pet_and_ownership_is_assigned_server_side(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("add_pet"), {
            "name": "Pip",
            "species": "Rabbit",
        })

        self.assertRedirects(response, reverse("pet_detail", args=[Animal.objects.get(name="Pip").pk]))
        self.assertEqual(Animal.objects.get(name="Pip").owner, self.owner)

    def test_pet_detail_shows_medical_history_section(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("pet_detail", args=[self.pet.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Medical history")

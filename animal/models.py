from django.db import models
from account.models import User


class Animal(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="animals",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    species = models.CharField(max_length=100)

    breed = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
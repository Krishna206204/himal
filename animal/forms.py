from django import forms

from account.models import User
from .models import Animal


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ("name", "species", "breed", "age", "owner")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "species": forms.TextInput(attrs={"class": "form-control"}),
            "breed": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "owner": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_staff or user.is_superuser or user.role == User.ADMIN:
            self.fields["owner"].queryset = User.objects.filter(
                role=User.PET_OWNER
            ).order_by("username")
        else:
            self.fields.pop("owner")

from django import forms
from .models import User, VeterinarianProfile


class VeterinarianProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        required=False
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )

    class Meta:
        model = VeterinarianProfile
        fields = [
            "experience_years",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["phone"].initial = user.phone
        self.fields["address"].initial = user.address

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": (
                    "w-full px-4 py-3 border-2 border-slate-300 "
                    "rounded-lg focus:ring-2 focus:ring-emerald-500 "
                    "focus:border-emerald-500"
                )
            })

    def save(self, commit=True):
        profile = super().save(commit=False)

        profile.user.phone = self.cleaned_data["phone"]
        profile.user.address = self.cleaned_data["address"]

        if commit:
            profile.user.save()
            profile.save()

        return profile
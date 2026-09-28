from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from animal.models import Animal
from appointment.models import Appointment
from medical.models import MedicalRecord
from .models import PetOwnerProfile, User, VeterinarianProfile


def public_home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "public_home.html", {
        "veterinarian_count": User.objects.filter(
            role=User.VETERINARIAN,
            is_active=True,
        ).count(),
        "patient_count": Animal.objects.count(),
    })


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    role = forms.ChoiceField(choices=(
        (User.PET_OWNER, "Pet Owner"),
        (User.VETERINARIAN, "Veterinarian"),
    ))
    license_number = forms.CharField(max_length=100, required=False)
    specialization = forms.CharField(max_length=150, required=False)
    qualification = forms.CharField(max_length=200, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("That email address is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error("password", error)
        if password and cleaned.get("confirm_password") and password != cleaned["confirm_password"]:
            self.add_error("confirm_password", "Passwords do not match.")
        if cleaned.get("role") == User.VETERINARIAN:
            license_number = cleaned.get("license_number", "").strip()
            if not license_number:
                self.add_error("license_number", "A veterinary license number is required.")
            elif VeterinarianProfile.objects.filter(license_number=license_number).exists():
                self.add_error("license_number", "That license number is already registered.")
        return cleaned


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not request.POST.get("remember_me"):
                request.session.set_expiry(0)
            next_url = request.POST.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
                phone=data["phone"],
                address=data["address"],
            )
            if user.role == User.VETERINARIAN:
                VeterinarianProfile.objects.create(
                    user=user,
                    license_number=data["license_number"].strip(),
                    specialization=data["specialization"],
                    qualification=data["qualification"],
                )
            else:
                PetOwnerProfile.objects.create(user=user)
        messages.success(request, "Account created. You can now sign in.")
        return redirect("login")
    return render(request, "register.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    is_admin = user.is_staff or user.is_superuser or user.role == User.ADMIN
    if is_admin:
        today_appointments = Appointment.objects.filter(
            appointment_date__date=timezone.localdate()
        )
        context = {
            "total_users": User.objects.count(),
            "total_vets": User.objects.filter(role=User.VETERINARIAN).count(),
            "total_owners": User.objects.filter(role=User.PET_OWNER).count(),
            "total_animals": Animal.objects.count(),
            "total_appointments": Appointment.objects.count(),
            "pending_appointments": Appointment.objects.filter(status="PENDING").count(),
            "today_appointments": today_appointments.count(),
            "recent_appointments": Appointment.objects.select_related(
                "animal", "pet_owner", "veterinarian"
            ).order_by("-appointment_date")[:5],
            "recent_records": MedicalRecord.objects.select_related(
                "animal", "veterinarian__user"
            )[:5],
        }
        return render(request, "dashboards/admin_dashboard.html", context)

    if user.role == User.VETERINARIAN:
        profile = getattr(user, "veterinarian_profile", None)
        all_vet_appointments = Appointment.objects.filter(veterinarian=user)
        appointments = Appointment.objects.filter(
            veterinarian=user,
            appointment_date__gte=timezone.now(),
        ).exclude(status__in=("CANCELLED", "COMPLETED")).select_related(
            "animal", "pet_owner"
        ).order_by("appointment_date")[:5]
        records = MedicalRecord.objects.none()
        if profile:
            records = MedicalRecord.objects.filter(
                veterinarian=profile
            ).select_related("animal").order_by("-record_date")[:5]
        return render(request, "dashboards/vet_dashboard.html", {
            "vet_profile": profile,
            "appointments": appointments,
            "recent_records": records,
            "today_appointment_count": Appointment.objects.filter(
                veterinarian=user,
                appointment_date__date=timezone.localdate(),
            ).exclude(status="CANCELLED").count(),
            "pending_appointment_count": Appointment.objects.filter(
                veterinarian=user,
                status="PENDING",
            ).count(),
            "patient_count": Animal.objects.filter(
                appointments__veterinarian=user
            ).distinct().count(),
            "completed_appointment_count": all_vet_appointments.filter(
                status="COMPLETED"
            ).count(),
        })

    animals = Animal.objects.filter(owner=user).order_by("name")
    owner_appointments = Appointment.objects.filter(pet_owner=user)
    return render(request, "dashboards/owner_dashboard.html", {
        "my_animals": animals,
        "appointments": owner_appointments.select_related(
            "animal", "veterinarian"
        ).order_by("-appointment_date")[:5],
        "upcoming_appointments": owner_appointments.filter(
            appointment_date__gte=timezone.now(),
        ).exclude(status__in=("CANCELLED", "COMPLETED")).select_related(
            "animal", "veterinarian"
        ).order_by("appointment_date")[:3],
        "total_appointment_count": owner_appointments.count(),
        "pending_appointment_count": owner_appointments.filter(
            status="PENDING"
        ).count(),
        "medical_records": MedicalRecord.objects.filter(
            animal__owner=user
        ).select_related("animal", "veterinarian__user").order_by("-record_date")[:5],
    })

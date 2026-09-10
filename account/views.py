from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import User, VeterinarianProfile, PetOwnerProfile
from animal.models import Animal
from appointment.models import Appointment
from medical.models import MedicalRecord

# LOGI

def login_view(request):

    # Already logged in
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Remember me
            if request.POST.get("remember_me"):

                # Session remains active according to Django's
                # normal session configuration.
                pass

            else:

                # Session expires when browser is closed.
                request.session.set_expiry(0)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(request, "account/login.html")

# LOGOU

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")

# REGISTE

def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        role = request.POST.get(
            "role",
            User.PET_OWNER
        )

        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # Password validation

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "register.html"
            )

        # Username validation

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "register.html"
            )

        # Validate role

        valid_roles = [
            User.ADMIN,
            User.VETERINARIAN,
            User.PET_OWNER,
        ]

        if role not in valid_roles:

            messages.error(
                request,
                "Invalid user role."
            )

            return render(
                request,
                "register.html"
            )

        try:

            with transaction.atomic():

                # Create user

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    phone=phone,
                    address=address
                )

                # Veterinarian profile

                if role == User.VETERINARIAN:

                    VeterinarianProfile.objects.create(
                        user=user,

                        license_number=request.POST.get(
                            "license_number",
                            ""
                        ),

                        specialization=request.POST.get(
                            "specialization",
                            ""
                        ),

                        qualification=request.POST.get(
                            "qualification",
                            ""
                        ),

                        experience_years=(
                            request.POST.get(
                                "experience_years"
                            ) or 0
                        ),

                        joined_date=request.POST.get(
                            "joined_date"
                        ) or None
                    )

                # Pet owner profile

                elif role == User.PET_OWNER:

                    PetOwnerProfile.objects.create(
                        user=user,

                        emergency_contact_phone=request.POST.get(
                            "emergency_contact_phone",
                            ""
                        )
                    )

                # Admin

                # Admin does not require an additional profile.

            messages.success(
                request,
                "Account created successfully! Please log in."
            )

            return redirect("login")

        except Exception as e:

            messages.error(
                request,
                f"Error creating account: {str(e)}"
            )

    return render(
        request,
        "account/register.html"
    )

@login_required
def dashboard(request):

    user = request.user

    # ADMIN

    if (
        user.role == User.ADMIN
        or user.is_superuser
        or user.is_staff
    ):

        return redirect("admin-dashboard")

    # VETERINARIAN

    elif user.role == User.VETERINARIAN:

        return redirect("vet-dashboard")

    # PET OWNER

    return redirect("owner-dashboard")

# ADMIN DASHBOAR

@login_required
def admin_dashboard(request):

    user = request.user

    # Only admin can access this dashboard
    if not (
        user.role == User.ADMIN
        or user.is_superuser
        or user.is_staff
    ):

        messages.error(
            request,
            "You are not authorized to access the admin dashboard."
        )

        return redirect("dashboard")

    # Statistics

    total_users = User.objects.count()

    total_vets = User.objects.filter(
        role=User.VETERINARIAN
    ).count()

    total_owners = User.objects.filter(
        role=User.PET_OWNER
    ).count()

    total_animals = Animal.objects.count()

    # Recent appointments

    try:

        recent_appointments = (
            Appointment.objects
            .all()
            .order_by("-appointment_date")[:5]
        )

    except Exception:

        recent_appointments = (
            Appointment.objects.all()[:5]
        )

    # Recent medical records

    recent_records = (
        MedicalRecord.objects
        .all()
        .order_by("-id")[:5]
    )

    context = {

        "total_users": total_users,

        "total_vets": total_vets,

        "total_owners": total_owners,

        "total_animals": total_animals,

        "recent_appointments": recent_appointments,

        "recent_records": recent_records,

        "user_role": "ADMIN",
    }

    return render(
        request,
        "account/dashboard.html",
        context
    )

# VETERINARIAN DASHBOAR

@login_required
def vet_dashboard(request):

    user = request.user

    # Authorization

    if user.role != User.VETERINARIAN:

        messages.error(
            request,
            "You are not authorized to access the veterinarian dashboard."
        )

        return redirect("dashboard")

    # Veterinarian profile

    vet_profile = getattr(
        user,
        "veterinarian_profile",
        None
    )

    # Appointments

    try:

        appointments = (
            Appointment.objects
            .filter(veterinarian=user)
            .order_by("appointment_date")[:5]
        )

    except Exception:

        appointments = Appointment.objects.none()

    # Medical records

    if vet_profile:

        try:

            recent_records = (
                MedicalRecord.objects
                .filter(veterinarian=vet_profile)
                .order_by("-id")[:5]
            )

        except Exception:

            recent_records = MedicalRecord.objects.none()

    else:

        recent_records = MedicalRecord.objects.none()

    total_animals = Animal.objects.count()

    context = {

        "appointments": appointments,

        "recent_records": recent_records,

        "total_animals": total_animals,

        "vet_profile": vet_profile,

        "user_role": "VETERINARIAN",
    }

    return render(
        request,
        "account/dashboard.html",
        context
    )


@login_required
def owner_dashboard(request):

    user = request.user

    if user.role != User.PET_OWNER:

        messages.error(
            request,
            "You are not authorized to access the pet owner dashboard."
        )

        return redirect("dashboard")

    pet_owner_profile = getattr(
        user,
        "pet_owner_profile",
        None
    )

    try:

        my_animals = Animal.objects.filter(
            owner=user
        )

    except Exception:

        my_animals = Animal.objects.none()

    try:

        appointments = (
            Appointment.objects
            .filter(animal__in=my_animals)
            .order_by("appointment_date")[:5]
        )

    except Exception:

        appointments = Appointment.objects.none()

    try:

        medical_records = (
            MedicalRecord.objects
            .filter(animal__in=my_animals)
            .order_by("-id")[:5]
        )

    except Exception:

        medical_records = MedicalRecord.objects.none()

    context = {

        "my_animals": my_animals,

        "appointments": appointments,

        "medical_records": medical_records,

        "pet_owner_profile": pet_owner_profile,

        "user_role": "PET_OWNER",
    }
    return render(
        request,
        "account/owner_dashboard.html",
        context
    )
    


@login_required
def owner_profile(request):
    # Only Pet Owners can access this page
    if request.user.role != request.user.PET_OWNER:
        messages.error(request, "You are not authorized to view this profile.")
        return redirect("dashboard")

    user = request.user

    # Get Pet Owner profile if it exists
    pet_owner_profile = getattr(user, "pet_owner_profile", None)

    context = {
        "user": user,
        "pet_owner_profile": pet_owner_profile,
    }

    return render(request, "account/owner_profile.html", context)
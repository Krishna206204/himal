from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import User, VeterinarianProfile, PetOwnerProfile
from animal.models import Animal
from appointment.models import Appointment
from medical.models import MedicalRecord




def login_view(request):

    
    if request.method == "POST":

        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

        except User.DoesNotExist:
            user = None

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
            "Invalid email or password."
        )

    return render(request, "account/login.html")
# LOGOU

@login_required
def logout_view(request):

    logout(request)
    return redirect("login")

# REGISTE

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import render, redirect

from .models import PetOwnerProfile

User = get_user_model()


def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Password validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "account/register.html")

        # Username validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "account/register.html")

        # Email validation
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "account/register.html")

        try:
            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=User.PET_OWNER,
                    phone=phone,
                )

                PetOwnerProfile.objects.create(
                    user=user
                )

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

    return render(request, "account/register.html")


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
    if request.user.role != User.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to view this profile."
        )
        return redirect("dashboard")

    user = request.user

    # Get Pet Owner profile if it exists
    pet_owner_profile = getattr(
        user,
        "pet_owner_profile",
        None
    )

    # Create profile automatically if it doesn't exist
    if pet_owner_profile is None:
        pet_owner_profile = PetOwnerProfile.objects.create(
            user=user
        )

    context = {
        "user": user,
        "pet_owner_profile": pet_owner_profile,
    }

    return render(
        request,
        "account/owner_profile.html",
        context
    )


@login_required
def edit_owner_profile(request):

    # Only Pet Owners can access this page
    if request.user.role != User.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to edit this profile."
        )
        return redirect("dashboard")

    user = request.user

    # Get Pet Owner profile
    pet_owner_profile = getattr(
        user,
        "pet_owner_profile",
        None
    )

    # Create profile if it doesn't exist
    if pet_owner_profile is None:
        pet_owner_profile = PetOwnerProfile.objects.create(
            user=user
        )

    if request.method == "POST":

       
        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()


        emergency_contact_phone = request.POST.get(
            "emergency_contact_phone",
            ""
        ).strip()


        
        if not email:
            messages.error(
                request,
                "Email address is required."
            )

            return render(
                request,
                "account/edit_owner_profile.html",
                {
                    "user": user,
                    "pet_owner_profile": pet_owner_profile,
                }
            )


        email_exists = User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=user.pk
        ).exists()

        if email_exists:

            messages.error(
                request,
                "This email address is already being used."
            )

            return render(
                request,
                "account/edit_owner_profile.html",
                {
                    "user": user,
                    "pet_owner_profile": pet_owner_profile,
                }
            )


        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.address = address

        user.save()


       
        pet_owner_profile.emergency_contact_phone = (
            emergency_contact_phone
        )

        pet_owner_profile.save()


       
        messages.success(
            request,
            "Your profile has been updated successfully."
        )

        return redirect("owner-profile")


    context = {
        "user": user,
        "pet_owner_profile": pet_owner_profile,
    }

    return render(
        request,
        "account/edit_owner_profile.html",
        context
    )

def vet_login(request):

    # If already logged in
    if request.user.is_authenticated:

        if request.user.role == User.VETERINARIAN:
            return redirect("vet-dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "account/vet_login.html"
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Only Veterinarians can use this login
            if user.role != User.VETERINARIAN:

                messages.error(
                    request,
                    "This login is only for veterinarians."
                )

                return render(
                    request,
                    "account/vet_login.html"
                )

            login(request, user)

            messages.success(
                request,
                "Welcome back, Dr. {}.".format(
                    user.get_full_name()
                    if user.get_full_name()
                    else user.username
                )
            )

            return redirect("vet-dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "account/vet_login.html"
    )
    


@login_required
def vet_dashboard(request):

    user = request.user

    # Only veterinarians can access this dashboard
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

    # Appointments assigned to this veterinarian
    appointments = (
        Appointment.objects
        .filter(veterinarian=user)
        .select_related(
            "animal",
            "animal__owner"
        )
        .order_by(
            "appointment_date",
            "appointment_time"
        )
    )

    # Medical records created by this veterinarian
    if vet_profile:

        recent_records = (
            MedicalRecord.objects
            .filter(veterinarian=vet_profile)
            .select_related("animal")
            .prefetch_related("prescriptions")
            .order_by(
                "-record_date",
                "-id"
            )[:5]
        )

    else:

        recent_records = MedicalRecord.objects.none()

    # Statistics
    total_appointments = (
        Appointment.objects
        .filter(veterinarian=user)
        .count()
    )

    pending_appointments = (
        Appointment.objects
        .filter(
            veterinarian=user,
            status="PENDING"
        )
        .count()
    )

    confirmed_appointments = (
        Appointment.objects
        .filter(
            veterinarian=user,
            status="CONFIRMED"
        )
        .count()
    )

    completed_appointments = (
        Appointment.objects
        .filter(
            veterinarian=user,
            status="COMPLETED"
        )
        .count()
    )

    # Unique animals treated/booked with this veterinarian
    total_patients = (
        Animal.objects
        .filter(
            appointments__veterinarian=user
        )
        .distinct()
        .count()
    )

    context = {
        "vet_profile": vet_profile,

        "appointments": appointments[:5],

        "recent_records": recent_records,

        "total_appointments": total_appointments,

        "pending_appointments": pending_appointments,

        "confirmed_appointments": confirmed_appointments,

        "completed_appointments": completed_appointments,

        "total_patients": total_patients,
    }

    return render(
        request,
        "account/vet_dashboard.html",
        context
    )
    





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import VeterinarianProfileUpdateForm
from .models import User


@login_required
def vet_profile(request):

    if request.user.role != User.VETERINARIAN:
        return redirect("dashboard")

    profile = request.user.veterinarian_profile

    return render(
        request,
        "account/vet_profile.html",
        {
            "profile": profile,
        }
    )


@login_required
def edit_veterinarian_profile(request):

    if request.user.role != User.VETERINARIAN:
        return redirect("dashboard")

    profile = request.user.veterinarian_profile

    if request.method == "POST":

        form = VeterinarianProfileUpdateForm(
            request.POST,
            instance=profile,
            user=request.user
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect(
                "vet-profile"
            )

    else:

        form = VeterinarianProfileUpdateForm(
            instance=profile,
            user=request.user
        )

    return render(
        request,
        "account/edit_veterinarian_profile.html",
        {
            "form": form
        }
    )
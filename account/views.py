from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import User, VeterinarianProfile, PetOwnerProfile
from animal.models import Animal
from appointment.models import Appointment
from medical.models import MedicalRecord


# -----------------------------------------------------------------------------
# Authentication Views
# -----------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
                
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role', User.PET_OWNER)
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')

        try:
            with transaction.atomic():
                # Create custom User instance
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    phone=phone,
                    address=address
                )

                # Create specific profile based on selected role
                if role == User.VETERINARIAN:
                    VeterinarianProfile.objects.create(
                        user=user,
                        license_number=request.POST.get('license_number'),
                        specialization=request.POST.get('specialization'),
                        qualification=request.POST.get('qualification'),
                        experience_years=request.POST.get('experience_years') or 0
                    )
                elif role == User.PET_OWNER:
                    PetOwnerProfile.objects.create(
                        user=user,
                        emergency_contact_phone=request.POST.get('emergency_contact_phone')
                    )

                messages.success(request, "Account created successfully! Please log in.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")

    return render(request, 'register.html')


def forgot_password_view(request):
    return render(request, 'forgot_password.html')


# -----------------------------------------------------------------------------
# Dynamic Dashboard Routing
# -----------------------------------------------------------------------------

@login_required
def dashboard(request):
    user = request.user
    role_str = str(user.role).upper() if user.role else ""

    # 1. ADMIN DASHBOARD
    if role_str == User.ADMIN or user.is_superuser or user.is_staff:
        context = {
            "total_users": User.objects.count(),
            "total_vets": User.objects.filter(role=User.VETERINARIAN).count(),
            "total_owners": User.objects.filter(role=User.PET_OWNER).count(),
            "total_animals": Animal.objects.count(),
            "recent_appointments": Appointment.objects.all().order_by("-appointment_date")[:5] if hasattr(Appointment, 'appointment_date') else Appointment.objects.all()[:5],
            "recent_records": MedicalRecord.objects.all()[:5],
            "user_role": "ADMIN",
        }
        return render(request, "dashboards/admin_dashboard.html", context)

    # 2. VETERINARIAN DASHBOARD
    elif role_str == User.VETERINARIAN:
        vet_profile = getattr(user, 'veterinarian_profile', None)

        if vet_profile:
            appointments = Appointment.objects.filter(veterinarian=user).order_by("appointment_date")[:5]
            recent_records = MedicalRecord.objects.filter(veterinarian=vet_profile)[:5]
        else:
            appointments = Appointment.objects.none()
            recent_records = MedicalRecord.objects.none()

        context = {
            "appointments": appointments,
            "recent_records": recent_records,
            "total_animals": Animal.objects.count(),
            "vet_profile": vet_profile,
            "user_role": "VETERINARIAN",
        }
        return render(request, "dashboards/vet_dashboard.html", context)

    # 3. PET OWNER DASHBOARD
    else:
        my_animals = Animal.objects.filter(owner=user) if hasattr(Animal, 'owner') else Animal.objects.none()
        appointments = Appointment.objects.filter(animal__in=my_animals).order_by("appointment_date")[:5]
        medical_records = MedicalRecord.objects.filter(animal__in=my_animals)[:5]
        pet_owner_profile = getattr(user, 'pet_owner_profile', None)

        context = {
            "my_animals": my_animals,
            "appointments": appointments,
            "medical_records": medical_records,
            "pet_owner_profile": pet_owner_profile,
            "user_role": "PET_OWNER",
        }
        return render(request, "dashboards/owner_dashboard.html", context)
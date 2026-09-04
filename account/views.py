from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            
            # If "Remember Me" is not checked, expire session on browser close
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
                
            return redirect_by_role(user)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    # Registration logic goes here
    return render(request, 'register.html')

def forgot_password_view(request):
    return render(request, 'forgot_password.html')

def redirect_by_role(user):
    """Utility function to route logged-in users according to User.role"""
    if user.role == user.ADMIN:
        return redirect('admin_dashboard')
    elif user.role == user.VETERINARIAN:
        return redirect('vet_dashboard')
    else:
        return redirect('pet_owner_dashboard')

# Dummy views for role dashboards
@login_required
def admin_dashboard(request):
    return render(request, 'base.html', {'title': 'Admin Dashboard'})

@login_required
def vet_dashboard(request):
    return render(request, 'base.html', {'title': 'Veterinarian Dashboard'})

@login_required
def pet_owner_dashboard(request):
    return render(request, 'base.html', {'title': 'Pet Owner Dashboard'})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from account.models import User, VeterinarianProfile, PetOwnerProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        phone = request.POST.get('phone')
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
                # Create the custom User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    phone=phone
                )

                # Create profile based on selected role
                if role == User.VETERINARIAN:
                    license_number = request.POST.get('license_number')
                    specialization = request.POST.get('specialization')
                    VeterinarianProfile.objects.create(
                        user=user,
                        license_number=license_number,
                        specialization=specialization
                    )
                else:
                    PetOwnerProfile.objects.create(user=user)

                messages.success(request, "Account created successfully! You can now log in.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")

    return render(request, 'register.html')
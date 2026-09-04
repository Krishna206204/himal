from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    
    # Role-based redirection targets
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vet-dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('pet-owner-dashboard/', views.pet_owner_dashboard, name='pet_owner_dashboard'),
]
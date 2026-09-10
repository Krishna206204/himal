from django.urls import path

from . import views


urlpatterns = [

    # =
    path(
        "login/",
        views.login_view,
        name="login"
    ),
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
    path(
        "register/",
        views.register_view,
        name="register"
    ),
    path(
        "forgot-password/",
        views.forgot_password_view,
        name="forgot-password"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin-dashboard"
    ),
    path(
        "vet-dashboard/",
        views.vet_dashboard,
        name="vet-dashboard"
    ),
    path(
        "owner-dashboard/",
        views.owner_dashboard,
        name="owner-dashboard"
    ),
    
    path(
    "owner-profile/",
    views.owner_profile,
    name="owner_profile"
),

]
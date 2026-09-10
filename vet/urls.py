
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# Main project urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),  # Recommended
    path('', include('account.urls')),
    path('animals/', include('animal.urls')),
    path('appointments/', include('appointment.urls')),
    path('medical/', include('medical.urls')),
]
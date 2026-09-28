from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('available-slots/', views.available_slots, name='available_appointment_slots'),
    path('book/', views.create_appointment, name='create_appointment'),
    path('<int:pk>/status/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
]
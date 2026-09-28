from django.urls import path
from . import views

urlpatterns = [
    path('', views.pet_list, name='pet_list'),
    path('add/', views.add_pet, name='add_pet'),
    path('<int:pk>/', views.pet_detail, name='pet_detail'),
    path('<int:pk>/edit/', views.edit_pet, name='edit_pet'),
    path('<int:pk>/delete/', views.delete_pet, name='delete_pet'),
]
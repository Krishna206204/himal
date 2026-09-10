from django.urls import path
from . import views


urlpatterns = [

    path(
        "pets/",
        views.animal_list,
        name="animal_list"
    ),

    path(
        "pets/add/",
        views.add_animal,
        name="add_animal"
    ),

    path(
        "pets/edit/<int:id>/",
        views.edit_animal,
        name="edit_animal"
    ),

    path(
        "pets/delete/<int:id>/",
        views.delete_animal,
        name="delete_animal"
    ),

]
from django.urls import path
from . import views


urlpatterns = [

    path(
        "appointments/",
        views.owner_appointment_list,
        name="owner-appointments"
    ),

    path(
        "appointments/book/",
        views.book_appointment,
        name="book-appointment"
    ),

]
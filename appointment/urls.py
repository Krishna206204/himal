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
    
    path(
        "vet/appointments/",
        views.vet_appointment_list,
        name="vet-appointments"
    ),
    
    path(
        "vet/appointments/<int:appointment_id>/status/",
        views.vet_update_appointment_status,
        name="vet-update-appointment-status"
    ),

]
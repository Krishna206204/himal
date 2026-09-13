from django.urls import path
from . import views


urlpatterns = [

    
    path(
        "medical-records/",
        views.owner_medical_records,
        name="owner-medical-records"
    ),

    path(
        "medical-records/<int:id>/",
        views.owner_medical_record_detail,
        name="owner-medical-detail"
    ),

    path(
        "medical-records/<int:id>/download/",
        views.download_medical_report,
        name="download-medical-report"
    ),


    path(
        "vet/my-records/",
        views.vet_medical_records,
        name="vet-medical-records"
    ),

    
    path(
        "vet/my-records/<int:pk>/",
        views.vet_medical_record_detail,
        name="vet-medical-record-detail"
    ),
    
    
   # medical/urls.py

path(
    "vet/medical-record/create/",
    views.create_medical_record,
    name="create-medical-record"
),


path(
    "vet/medical-record/<int:pk>/delete/",
    views.delete_medical_record,
    name="delete-medical-record",
),
    
    
    
]
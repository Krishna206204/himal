from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from account.models import User
from .forms import MedicalRecordForm, PrescriptionForm
from .models import MedicalRecord


def _is_admin(user):
    return user.is_staff or user.is_superuser or user.role == User.ADMIN


def _can_manage_records(user):
    return _is_admin(user) or user.role == User.VETERINARIAN


def _visible_records(user):
    records = MedicalRecord.objects.select_related(
        "animal", "animal__owner", "veterinarian__user"
    ).prefetch_related("prescriptions")
    if user.role == User.PET_OWNER and not _is_admin(user):
        return records.filter(animal__owner=user)
    if user.role == User.VETERINARIAN and not _is_admin(user):
        return records.filter(veterinarian__user=user)
    return records


@login_required
def medical_record_list(request):
    return render(request, "medical/medical_record_list.html", {
        "records": _visible_records(request.user),
        "can_manage": _can_manage_records(request.user),
    })


@login_required
def medical_record_detail(request, pk):
    record = get_object_or_404(_visible_records(request.user), pk=pk)
    return render(request, "medical/medical_record_detail.html", {
        "record": record,
        "prescription_form": PrescriptionForm(),
        "can_manage": _can_manage_records(request.user),
    })


@login_required
def add_medical_record(request):
    if not _can_manage_records(request.user):
        raise PermissionDenied
    veterinarian_profile = None
    if request.user.role == User.VETERINARIAN:
        veterinarian_profile = getattr(request.user, "veterinarian_profile", None)
        if veterinarian_profile is None:
            raise PermissionDenied
    if request.method == "POST":
        form = MedicalRecordForm(request.POST, user=request.user)
        if form.is_valid():
            record = form.save(commit=False)
            if request.user.role == User.VETERINARIAN:
                record.veterinarian = veterinarian_profile
            else:
                record.veterinarian = form.cleaned_data.get("veterinarian")
            if record.veterinarian is None:
                form.add_error("veterinarian", "Select the veterinarian who examined this pet.")
                return render(request, "medical/medical_record_form.html", {"form": form})
            if record.appointment_id and record.appointment.animal_id != record.animal_id:
                form.add_error("appointment", "Choose an appointment for this pet.")
                return render(request, "medical/medical_record_form.html", {"form": form})
            if (
                record.appointment_id
                and record.appointment.veterinarian_id != record.veterinarian.user_id
            ):
                form.add_error("appointment", "Choose an appointment with this veterinarian.")
                return render(request, "medical/medical_record_form.html", {"form": form})
            record.save()
            messages.success(request, f"Medical record created for {record.animal.name}.")
            return redirect("medical_record_detail", pk=record.pk)
    else:
        form = MedicalRecordForm(user=request.user)
    return render(request, "medical/medical_record_form.html", {"form": form})


@login_required
@require_POST
def add_prescription(request, pk):
    if not _can_manage_records(request.user):
        raise PermissionDenied
    record = get_object_or_404(_visible_records(request.user), pk=pk)
    form = PrescriptionForm(request.POST)
    if form.is_valid():
        prescription = form.save(commit=False)
        prescription.medical_record = record
        prescription.save()
        messages.success(request, "Prescription added.")
        return redirect("medical_record_detail", pk=pk)
    return render(request, "medical/medical_record_detail.html", {
        "record": record,
        "prescription_form": form,
        "can_manage": True,
    }, status=400)

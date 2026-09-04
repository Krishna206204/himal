from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MedicalRecord
from .forms import MedicalRecordForm, PrescriptionForm


@login_required
def medical_record_list(request):
    """Filter records: Pet owners see their animals' records; Vets/Admins see all."""
    if request.user.role == request.user.PET_OWNER:
        records = MedicalRecord.objects.filter(animal__owner__user=request.user)
    elif request.user.role == request.user.VETERINARIAN:
        records = MedicalRecord.objects.filter(veterinarian__user=request.user)
    else:
        records = MedicalRecord.objects.all()

    return render(request, "base.html", {"records": records})


@login_required
def medical_record_detail(request, pk):
    """View details of a specific record along with its prescriptions."""
    record = get_object_or_404(MedicalRecord, pk=pk)
    prescriptions = record.prescriptions.all()
    return render(request, "base.html", {"record": record, "prescriptions": prescriptions})


@login_required
def add_medical_record(request):
    """Create a new medical record (Veterinarian / Admin only)."""
    if request.method == "POST":
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"Medical record created for {record.animal.name}!")
            return redirect("medical_record_list")
    else:
        form = MedicalRecordForm()

    return render(request, "base.html", {"form": form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse

from .models import MedicalRecord, Prescription

from account.models import User, VeterinarianProfile
from appointment.models import Appointment

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# =========================================================
# OWNER - MEDICAL RECORD LIST
# =========================================================

@login_required
def owner_medical_records(request):

    if request.user.role != User.PET_OWNER:

        messages.error(
            request,
            "You are not authorized to view medical reports."
        )

        return redirect("dashboard")

    medical_records = (
        MedicalRecord.objects
        .filter(animal__owner=request.user)
        .select_related(
            "animal",
            "veterinarian",
            "appointment"
        )
        .prefetch_related("prescriptions")
        .order_by("-record_date", "-id")
    )

    return render(
        request,
        "medical/owner_medical_records.html",
        {
            "medical_records": medical_records
        }
    )


# =========================================================
# OWNER - MEDICAL RECORD DETAIL
# =========================================================

@login_required
def owner_medical_record_detail(request, id):

    if request.user.role != User.PET_OWNER:

        messages.error(
            request,
            "You are not authorized to view this medical report."
        )

        return redirect("dashboard")

    medical_record = get_object_or_404(
        MedicalRecord.objects
        .select_related(
            "animal",
            "veterinarian",
            "appointment"
        )
        .prefetch_related("prescriptions"),
        id=id,
        animal__owner=request.user
    )

    return render(
        request,
        "medical/owner_medical_detail.html",
        {
            "medical_record": medical_record
        }
    )


# =========================================================
# OWNER - DOWNLOAD PDF
# =========================================================

@login_required
def download_medical_report(request, id):

    if request.user.role != User.PET_OWNER:

        messages.error(
            request,
            "You are not authorized to download this report."
        )

        return redirect("dashboard")

    medical_record = get_object_or_404(
        MedicalRecord.objects
        .select_related(
            "animal",
            "animal__owner",
            "veterinarian",
            "veterinarian__user",
            "appointment"
        )
        .prefetch_related("prescriptions"),
        id=id,
        animal__owner=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    filename = (
        f"{medical_record.animal.name}"
        f"_medical_report.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=8,
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    story = []

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "HIMAL VET CARE",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Veterinary Medical Report",
            subtitle_style
        )
    )

    # -----------------------------------------------------
    # PET INFORMATION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Pet Information",
            heading_style
        )
    )

    owner_name = (
        medical_record.animal.owner.get_full_name()
        or medical_record.animal.owner.username
    )

    pet_data = [
        [
            Paragraph("<b>Pet Name</b>", small_style),
            Paragraph(
                str(medical_record.animal.name),
                small_style
            ),
        ],
        [
            Paragraph("<b>Species</b>", small_style),
            Paragraph(
                str(medical_record.animal.species),
                small_style
            ),
        ],
        [
            Paragraph("<b>Breed</b>", small_style),
            Paragraph(
                str(
                    medical_record.animal.breed
                    or "Not specified"
                ),
                small_style
            ),
        ],
        [
            Paragraph("<b>Age</b>", small_style),
            Paragraph(
                str(
                    medical_record.animal.age
                    or "Not specified"
                ),
                small_style
            ),
        ],
        [
            Paragraph("<b>Owner</b>", small_style),
            Paragraph(
                str(owner_name),
                small_style
            ),
        ],
    ]

    pet_table = Table(
        pet_data,
        colWidths=[
            45 * mm,
            125 * mm
        ]
    )

    pet_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#f1f5f9")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#cbd5e1")
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.3,
                colors.HexColor("#e2e8f0")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    story.append(pet_table)

    # -----------------------------------------------------
    # MEDICAL INFORMATION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Medical Information",
            heading_style
        )
    )

    veterinarian_name = "Not assigned"

    if medical_record.veterinarian:

        veterinarian_name = (
            medical_record.veterinarian.user.get_full_name()
            or medical_record.veterinarian.user.username
        )

    medical_data = [
        [
            Paragraph("<b>Record Date</b>", small_style),
            Paragraph(
                medical_record.record_date.strftime(
                    "%B %d, %Y"
                ),
                small_style
            ),
        ],
        [
            Paragraph("<b>Veterinarian</b>", small_style),
            Paragraph(
                str(veterinarian_name),
                small_style
            ),
        ],
        [
            Paragraph("<b>Diagnosis</b>", small_style),
            Paragraph(
                medical_record.diagnosis,
                small_style
            ),
        ],
        [
            Paragraph("<b>Symptoms</b>", small_style),
            Paragraph(
                medical_record.symptoms
                or "Not provided",
                small_style
            ),
        ],
        [
            Paragraph("<b>Treatment</b>", small_style),
            Paragraph(
                medical_record.treatment
                or "Not provided",
                small_style
            ),
        ],
        [
            Paragraph("<b>Notes</b>", small_style),
            Paragraph(
                medical_record.notes
                or "No additional notes",
                small_style
            ),
        ],
    ]

    medical_table = Table(
        medical_data,
        colWidths=[
            45 * mm,
            125 * mm
        ]
    )

    medical_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#f1f5f9")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#cbd5e1")
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.3,
                colors.HexColor("#e2e8f0")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    story.append(medical_table)

    # -----------------------------------------------------
    # PRESCRIPTIONS
    # -----------------------------------------------------

    prescriptions = medical_record.prescriptions.all()

    if prescriptions.exists():

        story.append(
            Paragraph(
                "Prescriptions",
                heading_style
            )
        )

        prescription_data = [
            [
                Paragraph("<b>Medicine</b>", small_style),
                Paragraph("<b>Dosage</b>", small_style),
                Paragraph("<b>Frequency</b>", small_style),
                Paragraph("<b>Duration</b>", small_style),
                Paragraph("<b>Instructions</b>", small_style),
            ]
        ]

        for prescription in prescriptions:

            prescription_data.append([
                Paragraph(
                    prescription.medicine_name,
                    small_style
                ),
                Paragraph(
                    prescription.dosage,
                    small_style
                ),
                Paragraph(
                    prescription.frequency,
                    small_style
                ),
                Paragraph(
                    prescription.duration,
                    small_style
                ),
                Paragraph(
                    prescription.instructions or "—",
                    small_style
                ),
            ])

        prescription_table = Table(
            prescription_data,
            colWidths=[
                35 * mm,
                27 * mm,
                30 * mm,
                25 * mm,
                53 * mm,
            ],
            repeatRows=1
        )

        prescription_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#f1f5f9")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#cbd5e1")
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor("#e2e8f0")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
            ])
        )

        story.append(prescription_table)

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "This report was generated from the "
            "Himal Vet Care veterinary management system.",
            subtitle_style
        )
    )

    document.build(story)

    return response


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import MedicalRecord


@login_required
def vet_medical_records(request):

    vet = request.user.veterinarian_profile

    records = MedicalRecord.objects.filter(
        veterinarian=vet
    ).select_related(
        "animal",
        "appointment"
    )

    return render(
        request,
        "medical/vet_medical_records.html",
        {
            "records": records
        }
    )


@login_required
def vet_medical_record_detail(request, pk):

    vet = request.user.veterinarian_profile

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        veterinarian=vet
    )

    return render(
        request,
        "medical/vet_medical_record_detail.html",
        {
            "record": record
        }
    )
    





from .forms import (
    MedicalRecordForm,
    PrescriptionForm
)

from .models import (
    MedicalRecord,
    Prescription
)
from account.models import User


@login_required
def create_medical_record(request):

    if request.user.role != User.VETERINARIAN:
        messages.error(
            request,
            "You are not authorized."
        )
        return redirect("dashboard")

    if request.method == "POST":

        record_form = MedicalRecordForm(
            request.POST,
            veterinarian=request.user
        )

        prescription_form = PrescriptionForm(
            request.POST
        )

        if (
            record_form.is_valid()
            and prescription_form.is_valid()
        ):

            appointment = (
                record_form.cleaned_data["appointment"]
            )

            record = record_form.save(commit=False)

            record.animal = appointment.animal

            record.veterinarian = (
                request.user.veterinarian_profile
            )

            record.appointment = appointment

            record.save()

            prescription = (
                prescription_form.save(commit=False)
            )

            prescription.medical_record = record

            prescription.save()

            messages.success(
                request,
                "Medical report and prescription created successfully."
            )

            return redirect(
                "vet-medical-records"
            )

    else:

        record_form = MedicalRecordForm(
            veterinarian=request.user
        )

        prescription_form = PrescriptionForm()

    return render(
        request,
        "medical/create_medical_record.html",
        {
            "record_form": record_form,
            "prescription_form": prescription_form,
        }
    )
    


@login_required
def delete_medical_record(request, pk):

    if request.user.role != User.VETERINARIAN:
        messages.error(request, "You are not authorized.")
        return redirect("dashboard")

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        veterinarian=request.user.veterinarian_profile
    )

    if request.method == "POST":
        record.delete()

        messages.success(
            request,
            "Medical record deleted successfully."
        )

    return redirect("vet-medical-records")
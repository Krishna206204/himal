from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Animal


@login_required
def animal_list(request):
    """
    Show only the logged-in owner's animals.
    """

    if request.user.role != request.user.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect("dashboard")

    animals = Animal.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "animal/animal_list.html",
        {
            "animals": animals
        }
    )

@login_required
def add_animal(request):
    """
    Add a new animal for the logged-in owner.
    """

    if request.user.role != request.user.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to add an animal."
        )
        return redirect("dashboard")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        species = request.POST.get("species", "").strip()
        breed = request.POST.get("breed", "").strip()
        age = request.POST.get("age", "").strip()
        symptoms = request.POST.get("symptoms", "").strip()

        if not name or not species:
            messages.error(
                request,
                "Name and species are required."
            )

            return render(
                request,
                "animal/add_animal.html"
            )

        Animal.objects.create(
            owner=request.user,
            name=name,
            species=species,
            breed=breed if breed else None,
            age=int(age) if age else None,
            symptoms=symptoms if symptoms else None
        )

        messages.success(
            request,
            "Pet added successfully."
        )

        return redirect("animal_list")

    return render(
        request,
        "animal/add_animal.html"
    )
    

@login_required
def edit_animal(request, id):
    """
    Edit only the logged-in owner's animal.
    """

    if request.user.role != request.user.PET_OWNER:

        messages.error(
            request,
            "You are not authorized to edit an animal."
        )

        return redirect("dashboard")


    animal = get_object_or_404(
        Animal,
        id=id,
        owner=request.user
    )


    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        species = request.POST.get(
            "species",
            ""
        ).strip()

        breed = request.POST.get(
            "breed",
            ""
        ).strip()

        age = request.POST.get(
            "age",
            ""
        ).strip()

        symptoms = request.POST.get(
            "symptoms",
            ""
        ).strip()


        # Required fields
        if not name or not species:

            messages.error(
                request,
                "Name and species are required."
            )

            return render(
                request,
                "animal/edit_animal.html",
                {
                    "animal": animal
                }
            )


        # Update animal
        animal.name = name

        animal.species = species

        animal.breed = (
            breed
            if breed
            else None
        )

        animal.age = (
            int(age)
            if age
            else None
        )

        animal.symptoms = (
            symptoms
            if symptoms
            else None
        )


        animal.save()


        messages.success(
            request,
            "Pet updated successfully."
        )


        return redirect("animal_list")


    return render(
        request,
        "animal/edit_animal.html",
        {
            "animal": animal
        }
    )

@login_required
def delete_animal(request, id):
    """
    Delete only the logged-in owner's animal.
    """

    if request.user.role != request.user.PET_OWNER:
        messages.error(
            request,
            "You are not authorized to delete an animal."
        )
        return redirect("dashboard")

    animal = get_object_or_404(
        Animal,
        id=id,
        owner=request.user
    )

    if request.method == "POST":

        animal.delete()

        messages.success(
            request,
            "Pet deleted successfully."
        )

        return redirect("animal_list")

    return render(
        request,
        "animal/delete_animal.html",
        {
            "animal": animal
        }
    )
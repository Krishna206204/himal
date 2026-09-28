from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from account.models import User
from .forms import AnimalForm
from .models import Animal


def _is_admin(user):
    return user.is_staff or user.is_superuser or user.role == User.ADMIN


@login_required
def pet_list(request):
    animals = Animal.objects.select_related("owner").order_by("name")
    if request.user.role == User.PET_OWNER and not _is_admin(request.user):
        animals = animals.filter(owner=request.user)
    return render(request, "animal/animal_list.html", {"animals": animals})


@login_required
def add_pet(request):
    if request.user.role not in (User.PET_OWNER, User.ADMIN) and not _is_admin(request.user):
        raise PermissionDenied
    form = AnimalForm(request.POST or None, user=request.user)
    if form.is_valid():
        animal = form.save(commit=False)
        if not _is_admin(request.user):
            animal.owner = request.user
        animal.save()
        messages.success(request, f"{animal.name} was added to the patient register.")
        return redirect("pet_detail", pk=animal.pk)
    return render(request, "animal/animal_form.html", {"form": form, "title": "Add a pet"})


@login_required
def pet_detail(request, pk):
    animal = get_object_or_404(
        Animal.objects.select_related("owner").prefetch_related("medical_records"),
        pk=pk,
    )
    if (
        request.user.role == User.PET_OWNER
        and not _is_admin(request.user)
        and animal.owner_id != request.user.id
    ):
        raise PermissionDenied
    can_manage = _is_admin(request.user) or animal.owner_id == request.user.id
    return render(
        request,
        "animal/animal_detail.html",
        {"animal": animal, "can_manage": can_manage},
    )


@login_required
def edit_pet(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    if not (_is_admin(request.user) or animal.owner_id == request.user.id):
        raise PermissionDenied
    form = AnimalForm(request.POST or None, instance=animal, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, f"{animal.name}'s details were updated.")
        return redirect("pet_detail", pk=animal.pk)
    return render(request, "animal/animal_form.html", {"form": form, "title": "Edit pet"})


@login_required
@require_POST
def delete_pet(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    if not (_is_admin(request.user) or animal.owner_id == request.user.id):
        raise PermissionDenied
    animal.delete()
    messages.success(request, "Pet record deleted.")
    return redirect("pet_list")
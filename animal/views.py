from django.http import HttpResponse

def pet_list(request):
    return HttpResponse("Pet List Page")

def add_pet(request):
    return HttpResponse("Add Pet Page")

def pet_detail(request, pk):
    return HttpResponse(f"Pet Detail Page for ID: {pk}")
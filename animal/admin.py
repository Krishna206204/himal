from django.contrib import admin

# Register your models here.
from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display=(
        'name',
        'species',
        'breed',
        'age',
        'owner',
        'created_at'
    )
    list_filter = ('species',)
    search_fields = ('name', 'species', 'breed', 'owner__username')
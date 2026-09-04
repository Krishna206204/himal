from django.db import models

# Create your models here.
class Animal(models.Model):
    name=models.CharField(max_length=100)
    species=models.CharField(max_length=100)
    breed=models.CharField(max_length=100,null=True)
    age=models.PositiveIntegerField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.name
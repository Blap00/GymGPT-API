from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False)  # Hacer el email único
    weight = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=10, null=True)
    def __str__(self):
        return str(self.id)
    
# Feedback info

class FeedbackModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=25, null=False)
    last_name = models.CharField(max_length=25, null=False)
    email = models.EmailField(max_length=60, null=False)
    feedback = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)


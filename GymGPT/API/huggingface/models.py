from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=150)
    mail = models.CharField(max_length=128)
    def __str__(self):
        return str(self.id)

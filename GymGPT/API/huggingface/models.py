from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    weight = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=10, null=True)
    def __str__(self):
        return str(self.id)

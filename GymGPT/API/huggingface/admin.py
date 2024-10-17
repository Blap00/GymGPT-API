from django.contrib import admin

from .models import *

@admin.register(OpenAIConfig)
class OpenAIConfigAdmin(admin.ModelAdmin):
    list_display = ('model', 'temperature', 'max_tokens')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email','image','age','weight','height','gender')
from django.contrib import admin

from .models import OpenAIConfig

@admin.register(OpenAIConfig)
class OpenAIConfigAdmin(admin.ModelAdmin):
    list_display = ('model', 'temperature', 'max_tokens')
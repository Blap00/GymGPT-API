# Generated by Django 5.1 on 2024-10-21 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('huggingface', '0005_openaiconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='openaiconfig',
            name='use',
            field=models.CharField(default='Ninguno', help_text='Cual es el Uso de esta configuración', max_length=50),
        ),
    ]

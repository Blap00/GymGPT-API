# Generated by Django 5.1 on 2024-10-21 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('huggingface', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machineinfogeneratedai',
            name='nom_maquina',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='machineinfogeneratedai',
            name='tipo_maquina',
            field=models.TextField(),
        ),
    ]

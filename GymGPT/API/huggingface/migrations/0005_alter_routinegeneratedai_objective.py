# Generated by Django 5.1 on 2024-11-09 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('huggingface', '0004_routinegeneratedai_objective'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routinegeneratedai',
            name='objective',
            field=models.CharField(default='', max_length=50),
        ),
    ]

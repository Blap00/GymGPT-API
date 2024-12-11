# Generated by Django 5.1 on 2024-12-10 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('huggingface', '0007_customuser_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

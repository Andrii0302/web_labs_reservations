# Generated by Django 5.2 on 2025-04-26 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_rooms", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]

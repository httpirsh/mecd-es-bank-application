# Generated by Django 4.2.17 on 2024-12-30 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_loanevaluation_timeslot"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="loanevaluation",
            name="timeslot",
        ),
        migrations.AddField(
            model_name="loanevaluation",
            name="timeslots",
            field=models.TextField(blank=True, null=True),
        ),
    ]

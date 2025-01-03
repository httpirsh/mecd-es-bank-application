# Generated by Django 4.2.17 on 2024-12-30 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_remove_loanevaluation_timeslot_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loanevaluation",
            name="status",
            field=models.CharField(
                choices=[
                    ("accept", "Accepted"),
                    ("interview", "Interview"),
                    ("reject", "Rejected"),
                ],
                max_length=11,
            ),
        ),
    ]

# Generated by Django 5.1.4 on 2025-05-12 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("simulation_manager", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="simulation",
            name="status",
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 5.0.14 on 2025-05-30 14:25

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(default="job", max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("QD", "QUEUED"),
                            ("PR", "PREPARING"),
                            ("FR", "FETCHING_RESOURCES"),
                            ("ST", "STARTING"),
                            ("RN", "RUNNING"),
                            ("PD", "PAUSED"),
                            ("CU", "CLEANING_UP"),
                            ("UR", "UPLOADING_RESULTS"),
                            ("SD", "SUCCEEDED"),
                            ("FD", "FAILED"),
                            ("FS", "FAILED_RESOURCE_ERROR"),
                            ("FM", "FAILED_TERMINATED"),
                            ("FO", "FAILED_TIMEOUT"),
                        ],
                        default="QD",
                        max_length=2,
                    ),
                ),
                ("yaml_file", models.FileField(upload_to="yaml_files/")),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

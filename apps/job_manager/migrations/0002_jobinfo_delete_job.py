# Generated by Django 5.0.14 on 2025-05-30 14:48

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job_manager", "0001_initial"),
        ("runner_manager", "0004_remove_runnerinfo_active_jobs"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JobInfo",
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
                    "assigned_runner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="runner_manager.runnerinfo",
                    ),
                ),
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
        migrations.DeleteModel(
            name="Job",
        ),
    ]

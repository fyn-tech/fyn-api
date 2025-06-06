# Generated by Django 5.0.14 on 2025-05-31 13:30

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("runner_manager", "0005_runnerinfo_1"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="runnerinfo",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="runnerinfo",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="runner_1",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="runnerinfo",
            name="state",
            field=models.CharField(
                choices=[
                    ("ID", "IDLE"),
                    ("BS", "BUSY"),
                    ("OF", "OFFLINE"),
                    ("UR", "UNREGISTERED"),
                ],
                default="UR",
                max_length=20,
            ),
        ),
        migrations.DeleteModel(
            name="RunnerInfo_1",
        ),
    ]

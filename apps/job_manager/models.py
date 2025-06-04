from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage as storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid
import os
from application_registry.models import AppInfo

class JobStatus(models.TextChoices):
    QUEUED = "QD", _("QUEUED")
    PREPARING = "PR", _("PREPARING")
    FETCHING_RESOURCES = "FR", _("FETCHING_RESOURCES")
    STARTING = "ST", _("STARTING")
    RUNNING = "RN", _("RUNNING")
    PAUSED = "PD", _("PAUSED")
    CLEANING_UP = "CU", _("CLEANING_UP")
    UPLOADING_RESULTS = "UR", _("UPLOADING_RESULTS")
    SUCCEEDED = "SD", _("SUCCEEDED")
    FAILED = "FD", _("FAILED")
    FAILED_RESOURCE_ERROR = "FS", _("FAILED_RESOURCE_ERROR")
    FAILED_TERMINATED = "FM", _("FAILED_TERMINATED")
    FAILED_TIMEOUT = "FO", _("FAILED_TIMEOUT")
    FAILED_RUNNER_EXCEPTION = "FE", _("FAILED_RUNNER_EXCEPTION")


class JobInfo(models.Model):

    # Meta data
    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4, 
                          editable=False,
                          help_text="Unique job identification number")
    name = models.CharField(max_length=100,
                            blank=False, 
                            null=False, 
                            default="job", 
                            help_text="User provided name for the job")
    priority = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Queueing priority, will determine position in remote runner's queue."
    )
    created_at = models.DateTimeField(auto_now_add=True, 
                                      editable=False,
                                      help_text="Creation date of the job.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date of last update.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="job", 
        editable=False,
        help_text="User who created the job."
    )
    status = models.CharField(
        default=JobStatus.QUEUED, 
        max_length=2, 
        choices=JobStatus.choices,
        help_text="Current status of the job."
    )

    # Job Execution Resources
    assigned_runner = models.ForeignKey(
        "runner_manager.RunnerInfo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    executable = models.CharField(
        default="",
        max_length=500,
        help_text="Path to executable or command name"
    )
    application_id = models.ForeignKey(
        AppInfo, 
        on_delete=models.CASCADE,
        null=True,
        help_text="The application id this job will execute"
    )
    command_line_args = models.JSONField(
        default=list,
        blank=True,
        help_text="List of command line arguments"
    )    
    working_directory = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Working directory (on the remote runner) for job execution"
    )

    # Simulation Inputs
    yaml_file = models.FileField(upload_to="yaml_files/")

    def __str__(self):
        return f"{self.id} {self.created_at} {self.updated_at} {self.created_by.username} {self.name} {self.yaml_file}"


def rename_yaml_file(instance, filename):
    ext = filename.split(".")[-1]  # get file extension
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("yaml_files", filename)


@receiver(pre_save, sender=JobInfo)
def update_filename(sender, instance, **kwargs):
    if instance.pk:
        initial_path = instance.yaml_file.path
        new_name = f"{instance.id}_simulation.yaml"

        if storage.exists(initial_path):
            storage.delete(new_name)  # Delete the file if it already exists
            storage.save(new_name, storage.open(initial_path))
            storage.delete(initial_path)

        instance.yaml_file.name = new_name

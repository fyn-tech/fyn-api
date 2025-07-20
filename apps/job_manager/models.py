# Copyright (C) 2025 fyn-api Authors
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
#  see <https://www.gnu.org/licenses/>.



import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
    application_id = models.ForeignKey(
        AppInfo, 
        on_delete=models.CASCADE,
        null=True,
        help_text="The application id this job will execute"
    )
    executable = models.CharField(
        default="",
        max_length=500,
        help_text="Path to executable or command name"
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

    # Local working directory - simplified
    local_working_directory = models.CharField(
        max_length=500,
        blank=True,
        editable=False,
        help_text="Local working directory path for this job"
    )

    # Job results/outputs
    exit_code = models.IntegerField(
        blank=True,
        null=True,
        help_text="The exit code of the application which was executed."
    )


    def save(self, *args, **kwargs):
        # Auto-generate local working directory path
        if not self.local_working_directory:
            self.local_working_directory = f"user_{self.created_by.id}/job_{self.id}"
        super().save(*args, **kwargs)

    def get_resources_by_type(self, resource_type):
        """Get all resources of a specific type"""
        return self.resources.filter(resource_type=resource_type)

    def get_input_files(self):
        """Get all input files"""
        return self.get_resources_by_type(ResourceType.INPUT)

    def get_resource_by_filename(self, filename):
        """Get resource by filename"""
        try:
            return self.resources.get(file__icontains=filename)
        except JobResource.DoesNotExist:
            return None

    def get_resource_url(self, filename):
        """Get URL for specific resource (for remote runner to download)"""
        resource = self.get_resource_by_filename(filename)
        return resource.file.url if resource else None

    @property
    def resource_summary(self):
        """Summary of resources by type for admin display"""
        summary = {}
        for choice in ResourceType.choices:
            resource_type = choice[0]
            count = self.resources.filter(resource_type=resource_type).count()
            if count > 0:
                summary[choice[1]] = count
        return summary

    def __str__(self):
        return f"{self.id} - {self.name} ({self.created_by.username})"

class ResourceType(models.TextChoices):
    INPUT = "IN", _("INPUT")
    OUTPUT = "OUT", _("OUTPUT") 
    CONFIG = "CFG", _("CONFIG")
    LOG = "LOG", _("LOG")
    TEMP = "TMP", _("TEMPORARY")
    RESULT = "RES", _("RESULT")

# Custom storage class - add this right after imports
class PreserveFilenameStorage(FileSystemStorage):
    """
    Custom storage that preserves original filenames and overwrites existing files.
    """
    
    def get_valid_name(self, name):
        """Return the original filename without Django's aggressive sanitization."""
        return os.path.basename(name)
    
    def get_available_name(self, name, max_length=None):
        """Allow overwrite of existing files instead of creating duplicates."""
        return name

# Create storage instance
preserve_storage = PreserveFilenameStorage()

def job_resource_upload_path(instance, filename):
    """
    Upload path relative to MEDIA_ROOT: user_{user_id}/job_{job_id}/filename
    Generates meaningful filenames when original filename is not useful
    """
    try:
        # Clean the filename to prevent issues
        clean_filename = os.path.basename(filename)
        
        # If filename is generic (like 'file') or empty, generate a better one
        if not clean_filename or clean_filename in ['file', 'upload']:
            if hasattr(instance, 'original_file_path') and instance.original_file_path:
                clean_filename = os.path.basename(instance.original_file_path)
            else:
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                resource_type = getattr(instance, 'resource_type', 'file')
                clean_filename = f"{instance.job.id}_{resource_type}_{timestamp}"
        
        return os.path.join(
            f"user_{instance.job.created_by.id}",
            f"job_{instance.job.id}",
            clean_filename
        )
    except (AttributeError, ValueError):
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join("temp_uploads", f"file_{timestamp}")

class JobResource(models.Model):
    """
    Simple model for job resources - all files go to root job directory
    """
    job = models.ForeignKey(
        JobInfo,
        on_delete=models.CASCADE,
        related_name="resources",
        help_text="Job this resource belongs to"
    )
    resource_type = models.CharField(
        max_length=3,
        choices=ResourceType.choices,
        default=ResourceType.INPUT,
        help_text="Type of resource (input, output, config, etc.)"
    )
    file = models.FileField(
        upload_to=job_resource_upload_path,
        storage=preserve_storage, 
        help_text="The actual file/resource"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional description of the resource"
    )
    original_file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Original file path where this resource was created (optional)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the resource was created/uploaded"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Who created/uploaded this resource (user or system)"
    )

    class Meta:
        ordering = ['resource_type', 'created_at']
        indexes = [
            models.Index(fields=['job', 'resource_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'file'],
                name='unique_job_file'
            )
        ]

    def __str__(self):
        return f"{self.job.name} - {self.get_resource_type_display()}: {self.filename}"

    @property
    def filename(self):
        """Return just the filename without path"""
        return self.file.name.split('/')[-1] if self.file else ""

    @property
    def full_file_path(self):
        """Return the full file system path for debugging"""
        try:
            return self.file.path if self.file else ""
        except (ValueError, AttributeError):
            return ""

    @property
    def file_url(self):
        """Return the URL to access this file"""
        try:
            return self.file.url if self.file else ""
        except (ValueError, AttributeError):
            return ""

    def delete(self, *args, **kwargs):
        """Override delete to ensure file is deleted from storage"""
        # Store file path before deleting the model instance
        if self.file:
            # Delete the file from storage
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
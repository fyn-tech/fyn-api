from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage as storage
import uuid
import os
from enum import Enum


class Status(Enum):
    IDLE = 'idle'
    BUSY = 'busy'
    OFFLINE = 'offline'


STATUS_CHOICES = [
    (status.value, status.name.title())
    for status in Status
]


class RunnerInfo(models.Model):

    # meta data
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(
        max_length=100, blank=False, null=False, default="")
    active_jobs = models.JSONField(default=list)
    state = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=Status.OFFLINE.value)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='runner')

    def __str__(self):
        raise NotImplementedError("WIP")


class HardwareInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    runner = models.ForeignKey(
        RunnerInfo, on_delete=models.CASCADE, related_name='hardware')

    def to_json(self):
        return {
            'id': self.id,
            'runner_id': self.runner.id,
        }

    def __str__(self):
        raise NotImplementedError("WIP")

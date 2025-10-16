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

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import JobInfo, JobStatus

@receiver(post_save, sender=JobInfo)
def notify_runner_on_new_job(sender, instance, created, **kwargs):
    """Notify runner when job is created or assigned"""
    if instance.assigned_runner and instance.status == JobStatus.QUEUED:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"runner_{instance.assigned_runner.id}",
            {
                "type": "job_notification",
                "job_id": str(instance.id),
                "message": "New job assigned"
            }
        )
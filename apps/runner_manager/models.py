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

import uuid

from django.conf import settings
from django.db import models


class RunnerStatus(models.TextChoices):
    IDLE = "ID", ("IDLE")
    BUSY = "BS", ("BUSY")
    OFFLINE = "OF", ("OFFLINE")
    UNREGISTERED = "UR", ("UNREGISTERED")


class RunnerInfo(models.Model):

    # meta data
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=100, blank=False, null=False, default="")
    state = models.CharField(
        max_length=20,
        default=RunnerStatus.UNREGISTERED.value,
        choices=RunnerStatus.choices,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="runner_1"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_contact = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Runner {self.id} - Owner: {self.owner} - State: {self.state}"


# ---------------------------------------------------------------------------------


class SystemInfo(models.Model):
    """
    Note: Units are base units, so Bytes no GB or MB. Conversions can be done
    in the client depending on need.
    """

    # Iding
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    runner = models.ForeignKey(
        RunnerInfo, on_delete=models.CASCADE, related_name="system"
    )

    # OS
    system_name = models.CharField(max_length=100, null=True)
    system_release = models.CharField(max_length=100, null=True)
    system_version = models.CharField(max_length=100, null=True)
    system_architecture = models.CharField(max_length=100, null=True)

    # CPU
    cpu_model = models.CharField(max_length=100, null=True)
    cpu_clock_speed_advertised = models.FloatField(null=True)
    cpu_clock_speed_actual = models.FloatField(null=True)
    cpu_logical_cores = models.IntegerField(null=True)
    cpu_physical_cores = models.IntegerField(null=True)
    cpu_cache_l1_size = models.IntegerField(null=True)
    cpu_cache_l2_size = models.IntegerField(null=True)
    cpu_cache_l3_size = models.IntegerField(null=True)

    # main memory
    ram_size_total = models.IntegerField(null=True)

    # disk
    disk_size_total = models.IntegerField(null=True)
    disk_size_available = models.IntegerField(null=True)

    # GPU info
    gpu_vendor = models.CharField(max_length=100, null=True)
    gpu_model = models.CharField(max_length=100, null=True)
    gpu_memory_size = models.IntegerField(null=True)
    gpu_clock_speed = models.FloatField(null=True)
    gpu_compute_units = models.IntegerField(null=True)
    gpu_core_count = models.IntegerField(null=True)
    gpu_driver_version = models.CharField(max_length=100, null=True)

    def to_json(self):
        return {
            "id": self.id,
            "runner_id": self.runner.id,
            "system_name": self.system_name,
            "system_release": self.system_release,
            "system_version": self.system_version,
            "system_architecture": self.system_architecture,
            "cpu_model": self.cpu_model,
            "cpu_clock_speed_advertised": self.cpu_clock_speed,
            "cpu_clock_speed_actual": self.cpu_clock_speed_actual,
            "cpu_logical_cores": self.cpu_logical_cores,
            "cpu_physical_cores": self.cpu_physical_cores,
            "cpu_cache_l1_size": self.cpu_cache_l1_size,
            "cpu_cache_l2_size": self.cpu_cache_l2_size,
            "cpu_cache_l3_size": self.cpu_cache_l3_size,
            "ram_size_total": self.ram_size_total,
            "disk_size_total": self.disk_size_total,
            "disk_size_available": self.disk_size_available,
            "gpu_vendor": self.gpu_vendor,
            "gpu_model": self.gpu_model,
            "gpu_memory_size": self.gpu_memory_size,
            "gpu_clock_speed": self.gpu_clock_speed,
            "gpu_compute_units": self.gpu_compute_units,
            "gpu_core_count": self.gpu_core_count,
            "gpu_driver_version": self.gpu_driver_version,
        }

    def __str__(self):
        return f"System {self.id} - Runner: {self.runner}"

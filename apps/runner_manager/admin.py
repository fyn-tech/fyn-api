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

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from runner_manager.models import RunnerInfo, SystemInfo
from job_manager.models import JobInfo


@admin.register(RunnerInfo)
class RunnerInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "token",
        "state",
        "get_system_name",
        "owner",
        "last_contact",
    )

    readonly_fields = (
        "assigned_jobs_list",
        "get_system_name",
    )

    def get_system_name(self, obj):
        """Get system name from related SystemInfo"""
        if hasattr(obj, "system") and obj.system.exists():
            system = obj.system.first()
            url = reverse("admin:runner_manager_systeminfo_change", args=[system.id])
            return format_html(
                '<a href="{}">{}</a> - {}', url, system.id, system.system_name
            )
        return "No system info"

    def assigned_jobs_list(self, obj):
        """Display all jobs assigned to this runner with job IDs as links"""
        assigned_jobs = JobInfo.objects.filter(assigned_runner=obj)
        if assigned_jobs:
            job_list = []
            for job in assigned_jobs:
                url = reverse("admin:job_manager_jobinfo_change", args=[job.id])
                job_link = format_html('<a href="{}">{}</a>', url, job.id)
                job_list.append(f"{job.name} (Status: {job.status}, ID: {job_link})")
            return format_html("<br>".join(job_list))
        return "No assigned jobs"

    get_system_name.short_description = "System Name"
    assigned_jobs_list.short_description = "All Queued Jobs"


@admin.register(SystemInfo)
class SystemInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "runner",
        "system_name",
        "system_release",
        "system_version",
        "system_architecture",
        "cpu_model",
        "cpu_clock_speed_advertised",
        "cpu_clock_speed_actual",
        "cpu_logical_cores",
        "cpu_physical_cores",
        "cpu_cache_l1_size",
        "cpu_cache_l2_size",
        "cpu_cache_l3_size",
        "ram_size_total",
        "disk_size_total",
        "disk_size_available",
        "gpu_vendor",
        "gpu_model",
        "gpu_memory_size",
        "gpu_clock_speed",
        "gpu_compute_units",
        "gpu_core_count",
        "gpu_driver_version",
    )
    list_filter = ("id",)
    ordering = ("id",)
    fieldsets = (
        ("ID", {"fields": ("id", "runner")}),
        (
            "Operating System",
            {
                "fields": (
                    "system_name",
                    "system_release",
                    "system_version",
                    "system_architecture",
                )
            },
        ),
        (
            "CPU System",
            {
                "fields": (
                    "cpu_model",
                    "cpu_clock_speed_advertised",
                    "cpu_clock_speed_actual",
                    "cpu_logical_cores",
                    "cpu_physical_cores",
                    "cpu_cache_l1_size",
                    "cpu_cache_l2_size",
                    "cpu_cache_l3_size",
                )
            },
        ),
        ("Memory", {"fields": ("ram_size_total",)}),
        ("Disk", {"fields": ("disk_size_total", "disk_size_available")}),
        (
            "GPU",
            {
                "fields": (
                    "gpu_vendor",
                    "gpu_model",
                    "gpu_memory_size",
                    "gpu_clock_speed",
                    "gpu_compute_units",
                    "gpu_core_count",
                    "gpu_driver_version",
                )
            },
        ),
    )
    readonly_fields = (
        "id",
        "runner",
    )

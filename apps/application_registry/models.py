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

from django.db import models


class AppType(models.TextChoices):
    UNKNOWN = "unknown", "unknown"
    PYTHON_SCRIPT = 'python', 'Python Script'
    LINUX_BINARY = 'linux_binary', 'Linux Binary'
    WINDOWS_BINARY = 'windows_binary', 'Windows Binary'
    SHELL_SCRIPT = 'shell', 'Shell Script'


class AppInfo(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identification number"
    )
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        default="job",
        help_text="User provided name for the application"
    )
    file_path = models.CharField(
        max_length=500,
        help_text="Full path to the application file"
    )
    type = models.CharField(
        default=AppType.UNKNOWN,
        max_length=20,
        choices=AppType.choices,
        help_text="Type of application program"
    )
    
    @property
    def content_type(self):
        """Return appropriate content type based on app_type."""
        content_type_map = {
            AppType.UNKNOWN: 'application/octet-stream',
            AppType.PYTHON_SCRIPT: 'text/x-python',
            AppType.SHELL_SCRIPT: 'text/x-shellscript',
            AppType.LINUX_BINARY: 'application/octet-stream',
            AppType.WINDOWS_BINARY: 'application/octet-stream',
        }
        return content_type_map.get(self.type, 'application/octet-stream')
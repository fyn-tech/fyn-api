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

from django.db import models
import uuid

class AppInfo(models.Model):
    
    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4, 
                          editable=False,
                          help_text="Unique identification number")
    name = models.CharField(max_length=100,
                            blank=False, 
                            null=False, 
                            default="job", 
                            help_text="User provided name for the job")
    file_path = models.FileField(upload_to="yaml_files/")

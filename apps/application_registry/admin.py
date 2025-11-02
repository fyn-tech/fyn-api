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
from .models import AppInfo


@admin.register(AppInfo)
class AppRegAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "application_type",
        "file_path",
        "schema_path",
        "executable_name",
        "default_cli_args",
        "use_mpi"
    )

    readonly_fields = (
        "id",
    )
    
    list_filter = ("application_type",)
    search_fields = ("name", "executable_name")
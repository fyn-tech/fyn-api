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

from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from .models import JobInfo, JobResource


class JobInfoSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = JobInfo
        fields = [
            "id",
            "name",
            "priority",
            "created_at",
            "updated_at",
            "status",
            "assigned_runner",
            "created_by",
        ]
        read_only_fields = ["updated_at", "created_by"]


class JobInfoRunnerSerializer(serializers.ModelSerializer):
    """Serializer for runners - excludes yaml_file which should be requested separately"""
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = JobInfo
        fields = [
            "id",
            "name", 
            "priority",
            "created_at",
            "updated_at",
            "created_by",
            "status",
            "assigned_runner",
            "application_id",
            "executable",
            "command_line_args",
            "resources",
            "working_directory",
            "exit_code"       
        ]
        read_only_fields = ["id", "name", "priority", "created_at",
                            "updated_at", "created_by", "assigned_runner",
                            "application_id", "executable", 
                            "command_line_args", "resources"]
        

class JobResourceSerializer(serializers.ModelSerializer):
    """For authenticated users - full CRUD access"""
    created_by = serializers.StringRelatedField(read_only=True)
    file = serializers.FileField(allow_empty_file=True)  # Allow empty files

    filename = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = JobResource
        fields = [
            "id",
            "job",
            "resource_type",
            "file",
            "description",
            "created_at",
            "created_by", 
            "filename",
            "file_url",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_filename(self, obj) -> str:
        """Return just the filename without path"""
        return obj.file.name.split('/')[-1] if obj.file else ""

    @extend_schema_field(OpenApiTypes.STR)
    def get_file_url(self, obj) -> str:
        """Return the URL to access this file"""
        try:
            return obj.file.url if obj.file else ""
        except (ValueError, AttributeError):
            return ""


class JobResourceRunnerSerializer(serializers.ModelSerializer):
    """For runners - read/upload access to assigned jobs"""
    download_url = serializers.SerializerMethodField()
    file = serializers.FileField(allow_empty_file=True)  # Allow empty files
    
    filename = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = JobResource
        fields = [
            "id",
            "job",
            "resource_type",
            "file",
            "description",
            "original_file_path",
            "filename", 
            "file_url",
            "download_url",
        ]
        read_only_fields = ["id", "filename", "file_url", "download_url"]
    
    @extend_schema_field(OpenApiTypes.STR)
    def get_download_url(self, obj) -> str:
        """Generate download URL for this resource"""
        request = self.context.get('request')
        if request and obj.id:
            return request.build_absolute_uri(f'/api/job_manager/resources/runner/{obj.id}/download/')
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_filename(self, obj) -> str:
        """Return just the filename without path"""
        return obj.file.name.split('/')[-1] if obj.file else ""

    @extend_schema_field(OpenApiTypes.STR)
    def get_file_url(self, obj) -> str:
        """Return the URL to access this file"""
        try:
            return obj.file.url if obj.file else ""
        except (ValueError, AttributeError):
            return ""
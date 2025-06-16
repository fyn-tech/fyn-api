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


class JobResourceRunnerSerializer(serializers.ModelSerializer):
    """For runners - read/upload access to assigned jobs"""
    download_url = serializers.SerializerMethodField()
    file = serializers.FileField(allow_empty_file=True)  # Allow empty files
    
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
    
    def get_download_url(self, obj):
        """Generate download URL for this resource"""
        request = self.context.get('request')
        if request and obj.id:
            return request.build_absolute_uri(f'/api/job_manager/resources/runner/{obj.id}/download/')
        return None
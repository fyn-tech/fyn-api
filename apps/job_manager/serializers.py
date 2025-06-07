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
            "application_id"
        ]
        read_only_fields = ["id", "name", "priority", "created_at", "updated_at", "created_by",
                            "assigned_runner", "application_id"]
        

class JobResourceSerializer(serializers.ModelSerializer):
    """For authenticated users - full CRUD access"""
    created_by = serializers.StringRelatedField(read_only=True)

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
    """For runners - minimal read/upload only"""
    
    class Meta:
        model = JobResource
        fields = [
            "job",
            "resource_type",
            "file",
            "filename", 
            "file_url",
        ]
        read_only_fields = ["filename", "file_url"]
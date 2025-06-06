from rest_framework import serializers
from .models import JobInfo


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
from rest_framework import serializers
from .models import JobInfo


class JobInfoSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = JobInfo
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "status",
            "assigned_runner",
            "created_by",
        ]
        read_only_fields = ["created_by"]

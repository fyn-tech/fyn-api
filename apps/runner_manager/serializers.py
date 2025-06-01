from rest_framework import serializers
from .models import RunnerInfo


class RunnerInfoFullSerializer(serializers.ModelSerializer):
    """_summary_
    Generally don't use this serialiser (it contains the auth token, so we don't want pass that around too much.)
    Args:
        serializers (_type_): _description_
    """

    class Meta:
        model = RunnerInfo
        fields = [
            "id",
            "state",
            "owner",
            "token",
            "created_at",
            "last_contact",
        ]
        read_only_fields = ["id", "owner", "created_at", "token"]


class RunnerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunnerInfo
        fields = [
            "id",
            "state",
            "owner",
            "created_at",
            "last_contact",
        ]
        read_only_fields = ["id", "owner", "created_at"]

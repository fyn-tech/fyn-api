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

from rest_framework import serializers

from .models import RunnerInfo


class RunnerInfoFullSerializer(serializers.ModelSerializer):
    """
    Full runner info serializer including auth token.
    
    Generally don't use this serializer - it contains the auth token,
    so we don't want to pass that around too much.
    """

    class Meta:
        model = RunnerInfo
        fields = [
            "id",
            "name",
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
            "name",
            "state",
            "owner",
            "created_at",
            "last_contact",
        ]
        read_only_fields = ["id", "owner", "created_at"]

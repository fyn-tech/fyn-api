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

import secrets

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    DjangoModelPermissionsOrAnonReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response

from .authentication import RunnerTokenAuthentication
from .models import RunnerInfo, RunnerStatus
from .permissions import IsAuthenticatedRunner
from .serializers import RunnerInfoFullSerializer, RunnerInfoSerializer


class RunnerManagerUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runners to be viewed or edited.
    """

    queryset = RunnerInfo.objects.all()
    serializer_class = RunnerInfoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly]

    @extend_schema(
        request=RunnerInfoSerializer, responses={201: RunnerInfoFullSerializer}
    )
    def create(self, request, *args, **kwargs):
        """
        If we create succefully we must return the new auth token.
        """
        serializer = RunnerInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        runner = serializer.save(owner=request.user, token=secrets.token_urlsafe(32))
        response_serializer = RunnerInfoFullSerializer(runner)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Users can only access their own runners"""
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            return RunnerInfo.objects.filter(owner=self.request.user)
        return RunnerInfo.objects.none()


class RunnerManagerRunnerViewSet(viewsets.ModelViewSet):
    serializer_class = RunnerInfoSerializer
    authentication_classes = [RunnerTokenAuthentication]
    permission_classes = [IsAuthenticatedRunner]

    def get_queryset(self):
        """Runner can only access their own data"""
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            return RunnerInfo.objects.filter(owner=self.request.user)
        return RunnerInfo.objects.none()

    def get_object(self):
        """Ensure runner can only access their own data, regardless of requested ID"""
        try:
            # Always return the runner owned by the authenticated user
            # This prevents a runner from accessing another runner's data
            runner = RunnerInfo.objects.get(owner=self.request.user)
            return runner
        except RunnerInfo.DoesNotExist:
            raise NotFound("No runner found for this user")

    def retrieve(self, request, pk=None):
        """Get runner data - ignores pk and returns authenticated runner's data"""
        runner = self.get_object()
        serializer = self.get_serializer(runner)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """Update runner data - ignores pk and updates authenticated runner's data"""
        runner = self.get_object()
        serializer = self.get_serializer(runner, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def list(self, request):
        """Disable list endpoint for runners"""
        return Response(
            {
                "detail": (
                    "Runners cannot list all runners. "
                    "Use retrieve with your runner ID."
                )
            },
            status=405,
        )

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "token": {"type": "string"},
                },
                "required": ["id", "token"],
            }
        },
        responses={200: RunnerInfoFullSerializer},
        description="Register runner with initial token and receive permanent token",
    )
    @action(
        detail=False, methods=["post"], authentication_classes=[], permission_classes=[]
    )
    def register(self, request):
        """Register a new runner with initial token."""
        runner_id = request.data.get("id")
        initial_token = request.data.get("token")

        if not runner_id or not initial_token:
            return Response(
                {"error": "id and token required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            runner = RunnerInfo.objects.get(id=runner_id, token=initial_token)

            # Rotate token and activate
            runner.token = secrets.token_urlsafe(32)
            runner.state = RunnerStatus.IDLE.value
            runner.last_contact = timezone.now()
            runner.save()

            response_serializer = RunnerInfoFullSerializer(runner)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except RunnerInfo.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

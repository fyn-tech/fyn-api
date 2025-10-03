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

import json
import secrets

from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    DjangoModelPermissionsOrAnonReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response

from accounts.models import User
from runner_manager.models import RunnerInfo, RunnerStatus, SystemInfo

from .authentication import RunnerTokenAuthentication
from .permissions import IsAuthenticatedRunner
from .serializers import RunnerInfoSerializer


class RunnerManagerUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runners to be viewed or edited.
    """

    queryset = RunnerInfo.objects.all()
    serializer_class = RunnerInfoSerializer
    permission_classes = [
        IsAuthenticated,
        DjangoModelPermissionsOrAnonReadOnly
    ]

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

# -----------------------------------------------------------------------------
# Front End API
# -----------------------------------------------------------------------------


@login_required
def add_new_runner(request):
    """ """

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    # Create new runner
    runner = RunnerInfo.objects.create(
        owner=request.user,
        token=secrets.token_urlsafe(32),
        state=RunnerStatus.UNREGISTERED.value,
    )

    return JsonResponse({"id": str(runner.id), "token": runner.token}, status=201)


@login_required
def delete_runner(request):
    """ """
    if request.method != "DELETE":
        return JsonResponse({"error": "Only DELETE method is allowed"}, status=405)

    try:
        data = json.loads(request.body)

        if "id" not in data:
            return JsonResponse({"error": "Runner ID is required"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    runner = get_object_or_404(RunnerInfo, id=data["id"])
    if runner.owner != request.user:
        return JsonResponse(
            {
                "status": "error",
                "message": "Permission denied: You do not own this runner",
            },
            status=403,
        )
    runner.delete()

    return JsonResponse(
        {
            "status": "success",
        },
        status=200,
    )


@login_required
def get_system(request):
    """ """
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed"}, status=405)
    try:
        user_runners = RunnerInfo.objects.filter(owner=request.user)
        hardware = SystemInfo.objects.filter(runner_id__in=user_runners)
        return JsonResponse(
            {"status": "success", "data": [hw.to_json() for hw in hardware]}, status=200
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def request_new_job(request):
    raise NotImplementedError("WIP")


@login_required
def get_jobs(request):
    raise NotImplementedError("WIP")


@login_required
def get_status(request):
    """ """

    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed"}, status=405)
    try:
        user_runners = RunnerInfo.objects.filter(owner=request.user)
        runner_status = user_runners.values("id", "state", "last_contact")
        return JsonResponse(
            {"status": "success", "data": list(runner_status)}, status=200
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# -----------------------------------------------------------------------------
# Runner API
# -----------------------------------------------------------------------------


@csrf_exempt
def register(request, runner_id):
    """ """

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    runner = get_object_or_404(RunnerInfo, id=runner_id)

    try:
        token = request.headers.get("token")
        if not token:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Authentication token missing in headers",
                },
                status=401,
            )

        if runner.token != token:
            return JsonResponse(
                {"status": "error", "message": "Authentication failed"}, status=401
            )

        runner.token = secrets.token_urlsafe(32)
        runner.state = RunnerStatus.IDLE.value
        runner.last_contact = timezone.now()
        runner.save()

        return JsonResponse(
            {"status": "success", "id": str(runner.id), "token": runner.token},
            status=200,
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def update_system(request, runner_id):

    if request.method != "PUT":
        return JsonResponse({"error": "Only PUT method is allowed"}, status=405)

    runner = get_object_or_404(RunnerInfo, id=runner_id)

    if runner.state == RunnerStatus.UNREGISTERED.value:
        return JsonResponse(
            {"status": "error", "message": "Unregistered runner"}, status=401
        )

    try:

        token = request.headers.get("token")
        if not token:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Authentication token missing in headers",
                },
                status=401,
            )

        if runner.token != token:
            return JsonResponse(
                {"status": "error", "message": "Authentication failed"}, status=401
            )

        update_data = json.loads(request.body).copy()
        system_info = SystemInfo.objects.get_or_create(runner=runner)[0]

        # Protect against accidental keys in request
        if "id" in update_data:
            del update_data["id"]
        if "runner_id" in update_data:
            del update_data["runner_id"]

        # Update system_info fields directly
        for field, value in update_data.items():
            if hasattr(system_info, field):
                setattr(system_info, field, value)
            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Unknown SystemInfo field: {field}",
                    },
                    status=400,
                )

        # Save the updated system info
        system_info.save()

        runner.last_contact = timezone.now()
        runner.save()
        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def report_status(request, runner_id):
    """ """

    if request.method != "PATCH":
        return JsonResponse({"error": "Only PATCH method is allowed"}, status=405)

    runner = get_object_or_404(RunnerInfo, id=runner_id)

    if runner.state == RunnerStatus.UNREGISTERED.value:
        return JsonResponse(
            {"status": "error", "message": "Unregistered runner"}, status=401
        )

    try:
        token = request.headers.get("token")
        if not token:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Authentication token missing in headers",
                },
                status=401,
            )

        if runner.token != token:
            return JsonResponse(
                {"status": "error", "message": "Authentication failed"}, status=401
            )

        data = json.loads(request.body)
        if "state" not in data:
            return JsonResponse(
                {"status": "error", "message": "State is required in the request body"},
                status=400,
            )
        runner.last_contact = timezone.now()
        runner.state = RunnerStatus[data["state"]].value
        runner.save()

        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# -----------------------------------------------------------------------------
# Genearal (multi-use) API
# -----------------------------------------------------------------------------


def start_job(request):
    raise NotImplementedError("WIP")


def terminate_job(request):
    raise NotImplementedError("WIP")

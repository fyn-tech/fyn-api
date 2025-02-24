from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from runner_manager.models import HardwareInfo, RunnerInfo, Status
from accounts.models import User
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils import timezone

import secrets
import json


# -----------------------------------------------------------------------------
# Front End API
# -----------------------------------------------------------------------------


@login_required
def add_new_runner(request):
    """

    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'},
                            status=405)

    # Create new runner
    runner = RunnerInfo.objects.create(
        owner=request.user,
        token=secrets.token_urlsafe(32),
        state=Status.UNREGISTERED.value
    )

    return JsonResponse({
        'id': str(runner.id),
        'token': runner.token
    }, status=201)


@login_required
def get_hardware(request):
    """

    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method is allowed'},
                            status=405)
    try:
        user_runners = RunnerInfo.objects.filter(owner=request.user)
        hardware = HardwareInfo.objects.filter(runner_id__in=user_runners)
        return JsonResponse({
            'status': 'success',
            'data': [hw.to_json() for hw in hardware]
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def request_new_job(request):
    raise NotImplementedError("WIP")


@login_required
def get_jobs(request):
    raise NotImplementedError("WIP")


@login_required
def get_status(request):
    """

    """

    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method is allowed'},
                            status=405)
    try:
        user_runners = RunnerInfo.objects.filter(owner=request.user)
        runner_status = user_runners.values('id', 'state', 'last_contact')
        return JsonResponse({
            'status': 'success',
            'data': list(runner_status)
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# -----------------------------------------------------------------------------
# Runner API
# -----------------------------------------------------------------------------


def register(request, runner_id):
    """

    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'},
                            status=405)

    runner = get_object_or_404(RunnerInfo, id=runner_id)

    try:
        data = json.loads(request.body)
        if runner.token != data['token']:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication failed'
            }, status=401)

        runner.token = secrets.token_urlsafe(32)
        runner.state = Status.IDLE.value
        runner.last_contact = timezone.now()
        runner.save()

        return JsonResponse({
            'id': str(runner.id),
            'token': runner.token
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def hardware_update(request):
    raise NotImplementedError("WIP")


def report_status(request, runner_id):
    """

    """

    if request.method != 'PATCH':
        return JsonResponse({'error': 'Only PATCH method is allowed'},
                            status=405)

    runner = get_object_or_404(RunnerInfo, id=runner_id)

    if runner.state == Status.UNREGISTERED.value:
        return JsonResponse({
            'status': 'error',
            'message': 'Unregistered runner'
        }, status=401)

    try:
        data = json.loads(request.body)

        if runner.token != data['token']:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication failed'
            }, status=401)

        runner.last_contact = timezone.now()
        runner.state = Status(data['state'].lower()).value
        runner.save()

        return JsonResponse({
            'status': 'success'
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# -----------------------------------------------------------------------------
# Genearal (multi-use) API
# -----------------------------------------------------------------------------

def start_job(request):
    raise NotImplementedError("WIP")


def terminate_job(request):
    raise NotImplementedError("WIP")

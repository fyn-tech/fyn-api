from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from runner_manager.models import HardwareInfo, RunnerInfo, Status
from accounts.models import User
from django.forms import model_to_dict
import secrets


@login_required
def runners(request):

    raise NotImplementedError("TBD")
    if request.method == 'FETCH':

        # Get the config file and the name from the request
        yaml_file = request.FILES['yaml_file']
        name = request.POST['name']

        # Create the simulation object
        RunnerInfo = RunnerInfo.objects.create(
            created_by=request.user, name=name, yaml_file=yaml_file)

        return JsonResponse({'message': 'File received successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

# -------------------------------------------------------------------------------------------------
# Front End API
# -------------------------------------------------------------------------------------------------


@login_required
def add_new_runner(request):
    """

    """

    if request.method == 'POST':

        # Generate a secure token
        token = secrets.token_urlsafe(32)

        # Create new runner
        runner = RunnerInfo.objects.create(
            owner=request.user,
            token=token,
            state=Status.OFFLINE.value
        )

        return JsonResponse({
            'id': str(runner.id),
            'token': runner.token
        }, status=201)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@login_required
def get_hardware(request):
    """
    
    """
    if request.method == 'GET':
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
    else:
        return JsonResponse({'error': 'Only GET method is allowed'},
                             status=405)


@login_required
def request_new_job(request):
    raise NotImplementedError("WIP")


@login_required
def get_jobs(request):
    raise NotImplementedError("WIP")


@login_required
def get_status(request):
    raise NotImplementedError("WIP")


# -------------------------------------------------------------------------------------------------
# Runner API
# -------------------------------------------------------------------------------------------------


def register(request):
    raise NotImplementedError("WIP")


def hardware_update(request):
    raise NotImplementedError("WIP")


def report_status(request):
    raise NotImplementedError("WIP")


# -------------------------------------------------------------------------------------------------
# Genearal (multi-use) API
# -------------------------------------------------------------------------------------------------

def start_job(request):
    raise NotImplementedError("WIP")


def terminate_job(request):
    raise NotImplementedError("WIP")

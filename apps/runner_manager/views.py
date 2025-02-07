from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import RunnerInfo
from accounts.models import User
from django.forms import model_to_dict
import yaml

@login_required
def runners(request):

    raise NotImplementedError("TBD")
    if request.method == 'FETCH':
        
        # Get the config file and the name from the request
        yaml_file = request.FILES['yaml_file']
        name = request.POST['name']
        
        # Create the simulation object
        RunnerInfo = RunnerInfo.objects.create(created_by=request.user, name=name, yaml_file=yaml_file)
        
        return JsonResponse({'message': 'File received successfully'}, status=200)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import Simulation
from accounts.models import User
from django.forms import model_to_dict
import yaml

@login_required
def handle_simulation_submission_form(request):
    if request.method == 'POST':
        
        # Get the config file and the name from the request
        yaml_file = request.FILES['yaml_file']
        name = request.POST['name']
        
        # Create the simulation object
        simulation = Simulation.objects.create(created_by=request.user, name=name, yaml_file=yaml_file)
        
        return JsonResponse({'message': 'File received successfully'}, status=200)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# -------------------------------------------------------------------------------------------------
# Back End Requests
# -------------------------------------------------------------------------------------------------

def simulation_manager(request):
  template = loader.get_template('simulation_manager.html')
  return HttpResponse(template.render())

def get_all_simulations(request):
    all_simulations = Simulation.objects.all()
    template = loader.get_template('get_all_simulations.html')
    context = {
        'all_simulations': all_simulations,
    }
    return HttpResponse(template.render(context, request))

def get_simulation(request, id):
    simulation = Simulation.objects.get(id=id)
    simulation_dict = Simulation.objects.filter(id=id).values().first()
    
    # the simulation_dict is necessary to print the simulation object in the template. 
    # In this way the we can loop through the dictionary and print the key value pairs and the output will always be accurate, even if the model changes.
    # Perhaps there is a more efficient way to do this, but this is the best way I could think of.
    # even for the frontend it can be useful to have the simulation_dict variable available.
    with open(simulation.yaml_file.path, 'r') as file:
        yaml_content = yaml.safe_load(file)
    template = loader.get_template('get_simulation.html')
    context = {
        'simulation': simulation,
        'simulation_dict': simulation_dict,
        'yaml_content': yaml_content,
    }
    return HttpResponse(template.render(context, request))

def get_user_simulations(request, id):
    #user_simulations = Simulation.objects.filter(user_id=id).values()
    user = User.objects.get(id=id)
    user_simulations = user.simulations.all()
    template = loader.get_template('get_user_simulations.html')
    context = {
        'user_simulations': user_simulations,
        'user': user,
    }
    return HttpResponse(template.render(context, request))

def delete_simulation(request, id):
    simulation = Simulation.objects.get(id=id)
    simulation.delete()
    return JsonResponse({'status': 'success', 'message': 'Simulation deleted successfully'}, status=200)



from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# from .models import Simulation
from .serializers import SimulationSerializer

class SimulationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer

    @action(detail=True, methods=['get'])
    def author_books(self, request, pk=None):
        """
        Returns all books written by the same author as the specified book.
        """
        try:
            book = self.get_object()
        except Simulation.DoesNotExist:
            return Response(
                {"error": "Simulation not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        author_books = Simulation.objects.filter(author=book.author).exclude(id=book.id)
        serializer = self.get_serializer(author_books, many=True)
        return Response(serializer.data)
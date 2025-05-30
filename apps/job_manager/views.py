from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import JobInfo
from accounts.models import User
from django.forms import model_to_dict
import yaml


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# from .models import Simulation
from .serializers import JobInfoSerializer


class JobInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulations to be viewed or edited.
    """

    queryset = JobInfo.objects.all()
    serializer_class = JobInfoSerializer

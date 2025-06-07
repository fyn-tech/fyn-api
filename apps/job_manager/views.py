from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import JobInfo, JobResource
from accounts.models import User
from django.forms import model_to_dict
import yaml

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from runner_manager.authentication import RunnerTokenAuthentication
from runner_manager.permissions import IsAuthenticatedRunner

from .serializers import (
    JobInfoSerializer, 
    JobInfoRunnerSerializer,
    JobResourceSerializer,
    JobResourceRunnerSerializer
)


class JobInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows jobs to be viewed or edited.
    """
    queryset = JobInfo.objects.all()
    serializer_class = JobInfoSerializer


class JobInfoRunnerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for runners to view and update their assigned jobs.
    """
    serializer_class = JobInfoRunnerSerializer
    authentication_classes = [RunnerTokenAuthentication]
    permission_classes = [IsAuthenticatedRunner]
    
    def get_queryset(self):
        """Runner can only access jobs assigned to them"""
        if hasattr(self.request, 'user') and hasattr(self.request.user, '_runner_info'):
            return JobInfo.objects.filter(assigned_runner=self.request.user._runner_info)
        return JobInfo.objects.none()
    
    def update(self, request, *args, **kwargs):
        """Runners can only update status field"""
        if set(request.data.keys()) - {'status'}:
            return Response({"detail": "Runners can only update the 'status' field."}, status=400)
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Runners can only update status field"""
        if set(request.data.keys()) - {'status'}:
            return Response({"detail": "Runners can only update the 'status' field."}, status=400)
        return super().partial_update(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Runners cannot create jobs"""
        return Response({"detail": "Runners cannot create jobs."}, status=405)
    
    def destroy(self, request, *args, **kwargs):
        """Runners cannot delete jobs"""
        return Response({"detail": "Runners cannot delete jobs."}, status=405)


class JobResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users to manage job resources.
    """
    queryset = JobResource.objects.all()
    serializer_class = JobResourceSerializer


class JobResourceRunnerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for runners to access resources for their assigned jobs.
    """
    serializer_class = JobResourceRunnerSerializer
    authentication_classes = [RunnerTokenAuthentication]
    permission_classes = [IsAuthenticatedRunner]
    
    def get_queryset(self):
        """Runner can only access resources for jobs assigned to them"""
        if hasattr(self.request, 'user') and hasattr(self.request.user, '_runner_info'):
            return JobResource.objects.filter(job__assigned_runner=self.request.user._runner_info)
        return JobResource.objects.none()
    
    def update(self, request, *args, **kwargs):
        """Runners cannot modify existing resources"""
        return Response({"detail": "Runners cannot modify existing resources."}, status=405)
    
    def partial_update(self, request, *args, **kwargs):
        """Runners cannot modify existing resources"""
        return Response({"detail": "Runners cannot modify existing resources."}, status=405)
    
    def destroy(self, request, *args, **kwargs):
        """Runners cannot delete resources"""
        return Response({"detail": "Runners cannot delete resources."}, status=405)
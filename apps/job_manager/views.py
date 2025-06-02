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
from runner_manager.authentication import RunnerTokenAuthentication
from runner_manager.permissions import IsAuthenticatedRunner

# from .models import Simulation
from .serializers import JobInfoSerializer, JobInfoRunnerSerializer


class JobInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows simulations to be viewed or edited.
    """

    queryset = JobInfo.objects.all()
    serializer_class = JobInfoSerializer


class JobInfoRunnerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for runners to view and update their assigned jobs.
    Runners can only see jobs assigned to them and update job status.
    """
    
    serializer_class = JobInfoRunnerSerializer
    authentication_classes = [RunnerTokenAuthentication]
    permission_classes = [IsAuthenticatedRunner]
    
    def get_queryset(self):
        """Runner can only access jobs assigned to them"""
        if hasattr(self.request, 'user') and hasattr(self.request.user, '_runner_info'):
            print("found")
            return JobInfo.objects.filter(assigned_runner=self.request.user._runner_info)
        return JobInfo.objects.none()
    
    def update(self, request, *args, **kwargs):
        """Runners can only update status field"""
        if set(request.data.keys()) - {'status'}:
            return Response(
                {"detail": "Runners can only update the 'status' field."}, 
                status=400
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Runners can only update status field"""
        if set(request.data.keys()) - {'status'}:
            return Response(
                {"detail": "Runners can only update the 'status' field."}, 
                status=400
            )
        return super().partial_update(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Runners cannot create jobs"""
        return Response({"detail": "Runners cannot create jobs."}, status=405)
    
    def destroy(self, request, *args, **kwargs):
        """Runners cannot delete jobs"""
        return Response({"detail": "Runners cannot delete jobs."}, status=405)
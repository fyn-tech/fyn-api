from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from runner_manager.authentication import RunnerTokenAuthentication
from runner_manager.permissions import IsAuthenticatedRunner

from .models import JobInfo, JobResource
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
    
    _edit_set = {'status', 'working_directory', 'exit_code'}
    def get_queryset(self):
        """Runner can only access jobs assigned to them"""
        if hasattr(self.request, 'user') and hasattr(self.request.user, '_runner_info'):
            return JobInfo.objects.filter(assigned_runner=self.request.user._runner_info)
        return JobInfo.objects.none()
    
    def update(self, request, *args, **kwargs):
        """Runners can only update status field"""
        if set(request.data.keys()) - self._edit_set:
            return Response({"detail":"Runners can only update "
                             f"{self._edit_set}  fields."}, status=400)
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Runners can only update status field"""
        if set(request.data.keys()) - self._edit_set:
            return Response({"detail":"Runners can only update "
                             f"{self._edit_set}  fields."}, status=400)
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

import os
import mimetypes
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class JobResourceRunnerViewSet(viewsets.ModelViewSet):
    serializer_class = JobResourceRunnerSerializer
    authentication_classes = [RunnerTokenAuthentication]
    permission_classes = [IsAuthenticatedRunner]
    parser_classes = [MultiPartParser, FormParser]  # Enable file uploads
    
    def get_queryset(self):
        if hasattr(self.request, 'user') and hasattr(self.request.user, '_runner_info'):
            queryset = JobResource.objects.filter(job__assigned_runner=self.request.user._runner_info)
            
            # Filter by query params
            job_id = self.request.query_params.get('job_id')
            if job_id:
                queryset = queryset.filter(job__id=job_id)
            
            resource_type = self.request.query_params.get('resource_type')
            if resource_type:
                queryset = queryset.filter(resource_type=resource_type)
            
            filename = self.request.query_params.get('filename')
            if filename:
                queryset = queryset.filter(file__icontains=filename)
            
            return queryset
        return JobResource.objects.none()

    @extend_schema(
        parameters=[
            OpenApiParameter('job_id', OpenApiTypes.UUID, description='Filter by job ID'),
            OpenApiParameter('resource_type', OpenApiTypes.STR, description='Filter by resource type'),
            OpenApiParameter('filename', OpenApiTypes.STR, description='Filter by filename'),
        ],
        description='List resources for assigned jobs with optional filters'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Validate job assignment before creating resource"""
        job = serializer.validated_data['job']
        
        # Ensure runner can only upload to assigned jobs
        if not hasattr(self.request.user, '_runner_info') or job.assigned_runner != self.request.user._runner_info:
            raise serializers.ValidationError("You can only upload resources to jobs assigned to you.")
        
        # Set created_by to None for runner uploads (system upload)
        serializer.save(created_by=None)
    
    def perform_update(self, serializer):
        """Validate job assignment before updating resource"""
        job = serializer.validated_data.get('job', serializer.instance.job)
        
        # Ensure runner can only update resources for assigned jobs
        if not hasattr(self.request.user, '_runner_info') or job.assigned_runner != self.request.user._runner_info:
            raise serializers.ValidationError("You can only update resources for jobs assigned to you.")
        
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Runners cannot delete resources"""
        return Response({"detail": "Runners cannot delete resources."}, status=405)
    
    @extend_schema(
        responses={200: OpenApiTypes.BINARY},
        description='Download resource file'
    )
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        resource = self.get_object()
        
        if not resource.file or not os.path.exists(resource.file.path):
            raise Http404("File not found")
        
        content_type, _ = mimetypes.guess_type(resource.file.path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        return FileResponse(
            open(resource.file.path, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=resource.filename
        )
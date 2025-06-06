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

from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse, Http404
import os

# Add this import for proper OpenAPI schema
from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiResponse

from .serializers import AppSerializer
from .models import AppInfo


class AppRegViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows runners to be viewed (read-only).
    """

    queryset = AppInfo.objects.all()
    serializer_class = AppSerializer

    @extend_schema(
        description="Download the raw program file for a specific application. Returns the file content directly based on the application type.",
        responses={
            200: OpenApiResponse(
                description='Program file content (binary or text)',
                response={'type': 'string', 'format': 'binary'}
            ),
            404: OpenApiResponse(description='Program file not found')
        }
    )
    @action(detail=True, methods=['get'])
    def program(self, request, pk=None):
        """
        Get the raw program file content for a specific application.
        Returns the file content directly based on the application type.
        """
        app_info = self.get_object()
        
        try:
            # Handle both FileField paths and direct file paths
            if hasattr(app_info.file_path, 'path'):
                file_path = app_info.file_path.path
            else:
                file_path = str(app_info.file_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise Http404("Program file not found")
            
            # Read file in binary mode to handle both text and binary files
            with open(file_path, 'rb') as file:
                content = file.read()
            
            # Use the content_type property to get proper MIME type
            content_type = app_info.content_type
            
            # Create response with appropriate headers
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{app_info.name}"'
            
            return response
            
        except Exception as e:
            raise Http404(f"Error reading program file: {str(e)}")
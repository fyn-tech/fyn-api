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

import os

from django.http import HttpResponse, Http404
from drf_spectacular.openapi import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import AppInfo
from .serializers import AppSerializer


class AppRegViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows runners to be viewed (read-only).
    """

    queryset = AppInfo.objects.all()
    serializer_class = AppSerializer

    @extend_schema(
        description=(
            "Download the raw program file for a specific application. "
            "Returns the file content directly based on the application type."
        ),
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
            
            # Create response with appropriate headers
            response = HttpResponse(content, content_type=app_info.content_type)
            response['Content-Disposition'] = f'attachment; filename="{app_info.name}"'
            
            return response
            
        except Exception as e:
            raise Http404(f"Error reading program file: {str(e)}")
        

    @extend_schema(
        description=(
            "Get the JSON schema for a specific application. "
            "Returns the schema content as JSON."
        ),
        responses={
            200: OpenApiResponse(
                description='JSON schema content',
                response={'type': 'object'} 
            ),
            404: OpenApiResponse(description='Schema file not found')
        }
    )
    @action(detail=True, methods=['get'])
    def schema(self, request, pk=None):
        """
        Get the JSON schema content for a specific application.
        Returns the schema as parsed JSON data.
        """
        app_info = self.get_object()
        
        if not app_info.schema_path:
            raise Http404("No schema defined for this application")
        
        try:
            # Handle both FileField paths and direct file paths
            if hasattr(app_info.schema_path, 'path'):
                schema_path = app_info.schema_path.path
            else:
                schema_path = str(app_info.schema_path)
            
            # Check if file exists
            if not os.path.exists(schema_path):
                raise Http404("Schema file not found")
            
            # Read and parse JSON file
            with open(schema_path, 'r') as file:
                schema_data = json.load(file)
            
            # Return as JSON response
            return Response(schema_data)
            
        except json.JSONDecodeError as e:
            raise Http404(f"Invalid JSON in schema file: {str(e)}")
        except Exception as e:
            raise Http404(f"Error reading schema file: {str(e)}")
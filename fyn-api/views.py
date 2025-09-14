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

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie

from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializer import LoginSerializer

def home(request):
    template = loader.get_template("master.html")
    context = {}
    return HttpResponse(template.render(context, request))

# --------------------------------------------------------------------------------------------------
# Account Authentication Related 
# --------------------------------------------------------------------------------------------------

@extend_schema(
    responses={200: {'type': 'object', 'properties': {'csrf_token': {'type': 'string'}}}},
    summary="Get CSRF token",
    description="Get CSRF token for frontend authentication"
)
@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token_view(request):
    """Get CSRF token for frontend"""
    return Response({
        'csrf_token': get_token(request)
    })

@extend_schema(
    request=LoginSerializer,
    responses={
        200: {
            'type': 'object', 
            'properties': {
                'status': {'type': 'string'},
                'token': {'type': 'string'},
                'user_data': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                        'username': {'type': 'string'},
                        'first_name': {'type': 'string'},
                        'last_name': {'type': 'string'}
                    }
                }
            }
        }
    },
    summary="User login",
    description="Login user and create session"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint - creates session"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'status': 'error', 
            'message': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
    
        return Response({
                'status': 'success',
                'token': token.key,
                'user_data': {
                    'id': str(user.id),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
    else:
        return Response({
            'status': 'error', 
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    request=None, 
    responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}}}},
    summary="User logout", 
    description="Logout user and destroy session"
)
@api_view(['POST'])
def logout_view(request):
    """Logout endpoint - destroys session"""
    logout(request)  
    return Response({'status': 'success'})

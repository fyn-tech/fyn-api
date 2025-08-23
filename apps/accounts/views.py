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
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to manage their accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication] 

    def get_permissions(self):
        """Handle new user, allow request to create new user. """
        if self.action == 'create':  
            return [AllowAny()]
        elif self.action == 'list':
            return [IsAdminUser()] 
        return [IsAuthenticated()] 
    
    def get_queryset(self):
        """Users can only access their own data"""
        if self.action == 'list':
            return self.queryset  
        return self.queryset.filter(id=self.request.user.id)

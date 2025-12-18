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


from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import PasswordUpdateSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to manage their accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Handle new user, allow request to create new user."""
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        """No returning of lists of users."""
        raise MethodNotAllowed("GET")

    @extend_schema(
        request=PasswordUpdateSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
        description="Update user password - requires old password verification",
    )
    @action(detail=True, methods=["post"], url_path="update-password")
    def change_password(self, request, pk=None):
        """Update user password - requires old password verification"""
        user = self.get_object()

        # Ensure user can only change their own password
        if user != request.user:
            return Response(
                {"error": "You can only change your own password"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PasswordUpdateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

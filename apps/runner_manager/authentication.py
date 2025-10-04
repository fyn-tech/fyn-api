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

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.extensions import OpenApiAuthenticationExtension

from .models import RunnerInfo


class RunnerTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication for runner agents.
    Authenticates runner machines using their unique tokens.
    """

    def authenticate_credentials(self, key):
        try:
            runner = RunnerInfo.objects.select_related("owner").get(token=key)
        except RunnerInfo.DoesNotExist:
            raise AuthenticationFailed("Invalid runner token.")

        if not runner.owner.is_active:
            raise AuthenticationFailed("User account is disabled.")

        user = runner.owner
        user._runner_info = runner

        return (user, runner)


class RunnerTokenScheme(OpenApiAuthenticationExtension):
    target_class = 'runner_manager.authentication.RunnerTokenAuthentication'
    name = 'runnerTokenAuth'  # Unique name to avoid conflicts

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Token-based authentication for runner agents. Format: `Token <runner_token>`'
        }

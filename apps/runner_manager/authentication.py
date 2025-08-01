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

from .models import RunnerInfo


class RunnerTokenAuthentication(TokenAuthentication):
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

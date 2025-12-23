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

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from runner_manager import views

router = DefaultRouter()
router.register(
    r"runner_manager/users",
    views.RunnerManagerUserViewSet,
    basename="runner_manager_users",
)
router.register(
    r"runner_manager/runner",
    views.RunnerManagerRunnerViewSet,
    basename="runner_manager_runners",
)

urlpatterns = [
    path("", include(router.urls)),
]

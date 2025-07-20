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

from . import views

router = DefaultRouter()
router.register(
    r"job_manager/users", 
    views.JobInfoViewSet, 
    basename="job_manager_user"
)
router.register(
    r"job_manager/runner", 
    views.JobInfoRunnerViewSet, 
    basename="job_manager_runner"
)
router.register(
    r"job_manager/resources/users", 
    views.JobResourceViewSet, 
    basename="job_manager_resources_user"
)
router.register(
    r"job_manager/resources/runner", 
    views.JobResourceRunnerViewSet, 
    basename="job_manager_resources_runner"
)

urlpatterns = [
    path("", include(router.urls)),
]

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
    # front end api
    # add new runner.
    path("runner_manager/add_new_runner/", views.add_new_runner, name="add_new_runner"),
    path("runner_manager/delete_runner/", views.delete_runner, name="delete_runner"),
    path(
        "runner_manager/get_system/", views.get_system, name="get_system"
    ),  # get system info
    path(
        "runner_manager/request_new_job/", views.request_new_job
    ),  # new request new job
    path("runner_manager/get_jobs/", views.get_jobs),  # get jobs
    path(
        "runner_manager/get_status/", views.get_status, name="get_status"
    ),  # get runner state
    # runner api
    path(
        "runner_manager/register/<uuid:runner_id>", views.register, name="register"
    ),  # authenticate runner
    path(
        "runner_manager/update_system/<uuid:runner_id>",
        views.update_system,
        name="update_system",
    ),  # update hardware info
    path(
        "runner_manager/report_status/<uuid:runner_id>",
        views.report_status,
        name="report_status",
    ),  # runner hearbeat
    # general (i.e. both front and runner) api
    path("runner_manager/start_job/", views.start_job),  # start job
    path("runner_manager/terminate_job/", views.terminate_job),  # terminate job
]

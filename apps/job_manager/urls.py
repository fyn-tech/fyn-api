from django.urls import include, path
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"job_manager/users", views.JobInfoViewSet, basename="job_manager_user")
router.register(r"job_manager/runner", views.JobInfoRunnerViewSet, basename="job_manager_runner")
router.register(r"job_manager/resources/users", views.JobResourceViewSet, basename="job_manager_resources_user")
router.register(r"job_manager/resources/runner", views.JobResourceRunnerViewSet, basename="job_manager_resources_runner")

urlpatterns = [
    path("", include(router.urls)),
]

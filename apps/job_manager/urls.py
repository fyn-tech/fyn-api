from django.urls import include, path
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"job_manager", views.JobInfoViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

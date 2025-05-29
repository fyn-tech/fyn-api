from django.urls import include, path
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"job_manager", views.JobViewSet)

urlpatterns = [
    # General fyn-api
    path("job_submission/", views.handle_simulation_submission_form),
    # other app apis
    path("", include("accounts.urls")),
    # fyn-api admin api
    path("job_manager/", views.simulation_manager, name="job_manager"),
    path(
        "job_manager/get_all_simulations/",
        views.get_all_simulations,
        name="get_all_simulations",
    ),
    path(
        "job_manager/get_user_simulations/<uuid:id>",
        views.get_user_simulations,
        name="get_user_simulations",
    ),
    path(
        "job_manager/get_simulation/<uuid:id>",
        views.get_simulation,
        name="get_simulation",
    ),
    path(
        "job_manager/delete_simulation/<uuid:id>",
        views.delete_simulation,
        name="delete_simulation",
    ),
    path("", include(router.urls)),
]

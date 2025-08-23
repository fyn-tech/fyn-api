"""
URL configuration for fyn-api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from . import views

urlpatterns = [
    # Home and Admin
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    
    # Auth endpoints
    path('auth/csrf/', views.csrf_token_view, name='csrf-token'),
    path('auth/user/login/', views.login_view, name='login'),
    path('auth/user/logout/', views.logout_view, name='logout'),
    
    # App endpoints
    path("", include("accounts.urls")),
    path("", include("application_registry.urls")),
    path("", include("job_manager.urls")),
    path("", include("runner_manager.urls")),

    # OpenAPI endpoints
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")
]

from django.urls import include, path
from . import views

urlpatterns = [
    # General fyn-api
    #path('runners/', views.runners),

    # other app apis
    path('', include('accounts.urls')),

]
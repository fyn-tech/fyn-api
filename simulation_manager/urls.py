from django.urls import include, path
from . import views

urlpatterns = [
    # General fyn-api
    path('simulation_submission/', views.handle_simulation_submission_form),

    # other app apis
    path('', include('accounts.urls')),

    # fyn-api admin api
    path('simulation_manager/', views.simulation_manager, name='simulation_manager'),
    path('simulation_manager/get_all_simulations/', views.get_all_simulations, name='get_all_simulations'),
    path('simulation_manager/get_user_simulations/<uuid:id>', views.get_user_simulations, name='get_user_simulations'),
    path('simulation_manager/get_simulation/<uuid:id>', views.get_simulation, name='get_simulation'),
    path('simulation_manager/delete_simulation/<uuid:id>', views.delete_simulation, name='delete_simulation'),
]
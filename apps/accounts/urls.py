from django.urls import path
from . import views

urlpatterns = [
    # front end api
    path('register_user/', views.register_user, name='register_user'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('sign_out/', views.sign_out, name='sign_out'),
    
    # back end api
    path('', views.home, name='home'),
    path('admin/', views.admin, name='admin'),
    path('account_manager/', views.account_manager, name='account_manager'),
    path('account_manager/get_all_users/', views.get_all_users, name='get_all_users'),
    path('account_manager/get_all_users/get_user/<uuid:id>', views.get_user, name='get_user'),
    path('account_manager/get_all_users/get_user/delete_user/<uuid:id>', views.delete_user, name='delete_user'),
]
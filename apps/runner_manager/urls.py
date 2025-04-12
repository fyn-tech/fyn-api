from django.urls import include, path
from runner_manager import views

urlpatterns = [

    # front end api
    # add new runner.
    path('add_new_runner/', views.add_new_runner, name='add_new_runner'),
    path('delete_runner/', views.delete_runner, name='delete_runner'),
    path('get_system/', views.get_system,
         name='get_system'),  # get system info
    path('request_new_job/', views.request_new_job),  # new request new job
    path('get_jobs/', views.get_jobs),  # get jobs
    path('get_status/', views.get_status,
         name='get_status'),  # get runner state

    # runner api
    path('register/<uuid:runner_id>',
         views.register, name='register'),  # authenticate runner
    path('update_system/<uuid:runner_id>',
         views.update_system, name='update_system'),  # update hardware info
    path('report_status/<uuid:runner_id>',
         views.report_status, name='report_status'),  # runner hearbeat

    # general (i.e. both front and runner) api
    path('start_job/', views.start_job),  # start job
    path('terminate_job/', views.terminate_job),  # terminate job

    # other app apis
    path('', include('accounts.urls')),

]

from django.urls import re_path
from runner_manager.consumers import RunnerConsumer

websocket_urlpatterns = [
    re_path(r"ws/runner_manager/(?P<runner_id>[^/]+)$", RunnerConsumer.as_asgi()),
]

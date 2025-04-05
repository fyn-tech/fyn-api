from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/runner_mannger/(?P<runner_id>[^/]+)/$',
            consumers.RunnerConsumer.as_asgi()),
]

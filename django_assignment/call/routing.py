from django.urls import re_path
from . import consumer

call_websocket_urlpatterns = [
    re_path(r'ws/call/', consumer.CallConsumer.as_asgi()),
]
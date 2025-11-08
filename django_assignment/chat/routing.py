from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path(r"ws/room/<str:room_name>/<str:username>/", consumers.ChatConsumer.as_asgi())
]
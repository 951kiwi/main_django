from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path('ws/host_room/<int:room_id>/', ChatConsumer.as_asgi()),
]
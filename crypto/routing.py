from django.urls import re_path
from . import customer

websocket_urlpatterns = [
    re_path(r'ws/socket-server/', customer.ChatConsumer.as_asgi())
]
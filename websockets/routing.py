from django.urls import re_path
from .consumers.main_consumer import MainConsumer

websocket_urlpatterns = [
    re_path(r'^ws/main/$', MainConsumer.as_asgi()),
]
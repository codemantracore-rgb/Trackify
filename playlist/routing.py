from .consumers import RecommandationConsumer
from django.urls import path
websocket_urlpatterns=[
    path('ws/recommendations/',RecommandationConsumer.as_asgi())
]
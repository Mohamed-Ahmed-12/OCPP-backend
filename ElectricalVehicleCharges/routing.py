from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/evcharger/(?P<charger_id>\w+)/$", consumers.OCPPConsumer.as_asgi()),
]
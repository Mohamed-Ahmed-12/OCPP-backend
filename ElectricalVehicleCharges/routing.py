from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/evcharger/(?P<charger_id>\w+)/$", consumers.OCPPConsumer.as_asgi()), #for regular id >> 1 , 2
    re_path(r"ws/evcharger/(?P<charger_id>[0-9a-fA-F-]{36})/$", consumers.OCPPConsumer.as_asgi()), #for uuid >> cfcf351e-47ed-4e9a-93b1-62d2ce26d550
]
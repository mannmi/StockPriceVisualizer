# routing.py
# import consumers
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
# myapp/routing.py
from django.urls import re_path
from . import consumers

# path('ws/', consumers.EchoConsumer.as_asgi())

websocket_urlpatterns = [
    re_path(r'ws/message/$', consumers.EventConsumer.as_asgi()),
    # re_path(r'ws/event_triger/$', consumers.MessageConsumer.as_asgi()),

]

application = ProtocolTypeRouter({
    # Defines What Domains are allowed
    "websocket": AllowedHostsOriginValidator(
        # Gives acces to User (same as request.user)
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns

            )
        )
    ),
})

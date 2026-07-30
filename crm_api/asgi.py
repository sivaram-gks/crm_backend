"""
ASGI config for crm_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_api.settings')

# application = get_asgi_application()
django_asgi_app = get_asgi_application()
# ONLY AFTER Django is ready, import Channels stuff
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import telecalling.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            telecalling.routing.websocket_urlpatterns 
        )
    ),
})

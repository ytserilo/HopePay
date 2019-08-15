from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from .consumer import UserStatus
from Chat.consumer import ChatConsumer
from Remittance.consumer import RemittanceConsumer
from market.consumer import AuctionConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('market/about_product/<int:id>/', AuctionConsumer),
            path('chat/chat_room/<str:unique_link>/', ChatConsumer),
            path('userstatus/', UserStatus),
            path('remittance/<str:unique_link>/', RemittanceConsumer),
        ])
    ),
})

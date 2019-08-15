from django.urls import path
from HopePay.dh import DH
from .views import *

urlpatterns = [
    path('remittances/', Chats.as_view()),
    path('dh/', DH.as_view()),
    path('rsa/', RSACHat.as_view()),
    path('chat_room/<str:unique_link>/', ChatID.as_view()),
    path('read_messages/<str:unique_link>/', ReadMessages.as_view()),
]

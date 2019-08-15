from django.urls import path
from .views import *

urlpatterns = [
    path('orders/', Orders.as_view()),
]

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *

urlpatterns = [
    path('ask/', AskView.as_view()),
    path('not_found/', Error.as_view()),
    path('', Main.as_view()),
]

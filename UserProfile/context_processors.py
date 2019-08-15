from django.contrib.auth import get_user
from django.contrib import auth
from .models import CustomUser

def user(request):
    try:
        CustomUser.objects.get(id=auth.get_user(request).id)
        return {
            'user': CustomUser.objects.get(id=auth.get_user(request).id)
        }
    except:
        return {
            'user': None
        }

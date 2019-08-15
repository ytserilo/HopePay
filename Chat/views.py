from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from Remittance.models import Remittance
from UserProfile.models import UnreadMessage, CustomUser
from django.contrib import auth
from django.views import View
from .utils import *
import redis

rsa_key_storage = redis.Redis(host='localhost', port=6379, db=5)
# Create your views here.
class Chats(ChatsMixin):
    template = 'remittances.html'


class ChatID(ChatInRoomMixin):
    pass

class RSACHat(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        if request.is_ajax():
            data = request.POST
            public = data.get('public')
            key = data.get('key')
            
            rsa_key_storage.set(str(key), public)
            rsa_key_storage.expire(key, 86400)
            return JsonResponse({'result': 'ok'})

class ReadMessages(View):
    def get(self, request, unique_link):
        if request.is_ajax():
            try:
                remittance = Remittance.objects.get(unique_link=unique_link)
                user = CustomUser.objects.get(id=auth.get_user(request).id)
                UnreadMessage.objects.filter(remittance=remittance, user=user).delete()
                return JsonResponse({'result': 'all read'})
            except:
                return JsonResponse({'result': 'error'})

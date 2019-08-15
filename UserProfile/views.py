from django.shortcuts import render
from django.views import View
from .utils import *
from Crypto.PublicKey import RSA
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import redis, json, re, os

rsa_key_storage = redis.Redis(host='localhost', port=6379, db=5)
# Create your views here.
class LogOut(UserLogOutMixin):
    pass

class LoginIn(LoginInMixin):
    pass

class Register(UserRegisterMixin):
    pass

class EmailValidate(EmailValidatorMixin):
    pass

class EmailSend(SendMailPinCodeMixin):
    pass

class ChangePassword(UserChangePasswordMixin):
    pass

class AddPaymentCard(AddPaymentCardMixin):
    pass

class RestorePassword(ChangePasswordMixin):
    pass

class UserProfile(View):
    def get(self, request):
        return render(request, 'profile.html')

class RSAView(View):
    def get(self, request):
        if request.is_ajax():
            storage_key_in_the_database = request.GET.get('key')
            rsa_key = RSA.generate(1024)
            pubkey = re.sub(r'-----BEGIN PUBLIC KEY-----\n', '', str(rsa_key.publickey().exportKey().decode()))
            pubkey = re.sub(r'\n-----END PUBLIC KEY-----', '', pubkey)

            if rsa_key_storage.get(storage_key_in_the_database):
                return JsonResponse({'response': 'reload'})
            else:
                rsa_key_storage.set(storage_key_in_the_database, rsa_key.exportKey('PEM'))
                rsa_key_storage.expire(storage_key_in_the_database, 86400)
            return JsonResponse({'pubkey': pubkey, 'key': storage_key_in_the_database})

class ChangeImage(View):
    @method_decorator(csrf_protect)
    def post(self, request):
        if request.is_ajax():

            id = auth.get_user(request).id
            user = CustomUser.objects.filter(id=id)
            if len(user) > 0:
                user = user[0]
                file = request.FILES.get('file')

                if file.size // 1000 < 1000 and 'image' in file.content_type:
                    if user.user_image != 'user_image/default.png':
                        os.remove('media/'+str(user.user_image))
                    with open('media/user_image/'+file.name, 'wb') as image:
                        image.write(bytes(file.file.getvalue()))
                        user.user_image = 'user_image/' + file.name
                        user.save()
                    return JsonResponse({'result': 'ok'})
                else:
                    return JsonResponse({'result': 'Зображення не відповідає формату або завелике'})
            else:
                return JsonResponse({'result': 'Увійдіть або зареєструйтесь'})

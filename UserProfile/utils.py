from django.views import View
from liqpay.liqpay import LiqPay
from django.contrib import auth
from HopePay.celery import app
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .send_mail import SendMail
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from .forms import *
from .models import CustomUser, UserCard
import re, random, redis, json, uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import *
from django.contrib.auth.models import User

rsa_key_storage = redis.Redis(host='localhost', port=6379, db=5)

public_key = "sandbox_i15760037832"
private_key = b"sandbox_pHY01HT3S4gEcGtXOAJx1XKUDHZpOgtYhJNEcA6o"

def gen_link():
    random = None
    while True:
        random = re.sub(r'-', '', str(uuid.uuid4()))
        try:
            Remittance.objects.get(unique_link=random)
            continue
        except:
            break
    return random

def validgetdata(text, key):
    if text is None:
        text = ''
    if type(key) == str:
        key = key.encode()
    if type(text) == str:
        text = text.encode()

    rsakey = RSA.importKey(key)
    rsakey = PKCS1_v1_5.new(rsakey)
    text = b64decode(text)
    d = rsakey.decrypt(text, b'de')
    return d.decode()

class RedirectPersonalMixin(View):

    def get(self, request):
        username = auth.get_user(request).username
        args = {}
        if username:
            try:
                login = CustomUser.objects.get(username=username)
            except:
                args['error'] = 'Войдите или зарегестрируйтесь'
                return render(request, 'private_page.html', context=args)
        else:
            args['error'] = 'Войдите или зарегестрируйтесь'
            return render(request, 'private_page.html', context=args)
        return render(request, 'private_page.html')

class UserLogOutMixin(View):
    def get(self, request):
        auth.logout(request)
        return redirect('/chat/remittances/')

class UserRegisterMixin(View):
    email = None

    def get(self, request):

        if request.is_ajax():
            storage_key_in_the_database = request.GET.get('key')
            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            try:
                username = validgetdata(request.GET.get('username'), private_key)

                user = CustomUser.objects.get(username=username)

                return JsonResponse({
                    'result_login': 'Користувач з таким логіном існує'
                })
            except:
                re_login = r'^[a-zA-Z][a-zA-Z0-9-_\.]{2,20}$'
                try:
                    if len(username) < 3:
                        return JsonResponse({ 'result_login': 'Логін повинен мати не менше 3 символів' })

                    elif re.search(re_login, username) is None:
                        return JsonResponse({ 'result_login': 'Введіть логін використовуючи латиницю і цифри наприклад Ivanov123' })

                    else:
                        return JsonResponse({ 'result_login': 'OK' })
                except:
                    pass

            try:
                email = validgetdata(request.GET.get('email'), private_key)
                user = CustomUser.objects.get(custom_email=email)

                return JsonResponse({ 'result_email': 'Користувач з таким аресом електронної пошти вже існує' })
            except:
                re_email = r'^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$'
                try:
                    if re.search(re_email, email) is None:
                        return JsonResponse({ 'result_email': 'Введений вами адрес електронної пошти не відповідає формату example@postal.com' })
                    else:
                        return JsonResponse({ 'result_email': 'OK' })
                except:
                    pass

        reg_form = UserCreateForm()
        return render(request, 'register.html', context={
            'reg_form': reg_form
        })

    @method_decorator(csrf_protect)
    def post(self, request):
        if request.is_ajax():
            request_data = request.POST

            storage_key_in_the_database = request_data.get('key')
            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            username = validgetdata(request_data.get('username'), private_key)
            password = validgetdata(request_data.get('password2'), private_key)
            email = validgetdata(request_data.get('custom_email'), private_key)

            data = {
                'custom_email': email,
                'password2': password,
                'password1': validgetdata(request_data.get('password1'), private_key),
                'username': username,
                'first_name': validgetdata(request_data.get('first_name'), private_key),
                'last_name': validgetdata(request_data.get('last_name'), private_key),
            }

            reg_form = UserCreateForm(data)
            if reg_form.is_valid():
                if rsa_key_storage.get(email).decode() == 'ok':
                    user = reg_form.save()

                    auth.login(request, user)
                    rsa_key_storage.delete(email)
                    return JsonResponse({'result': 'ok'})
                else:
                    return JsonResponse({'result': 'no'})
            else:
                return JsonResponse({'result': 'no'})
        return HttpResponse("answer")


class LoginInMixin(View):

    @method_decorator(csrf_protect)
    def post(self, request):
        if request.is_ajax():
            storage_key_in_the_database = request.POST.get('key')
            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            args = {}
            username = validgetdata(request.POST.get('username'), private_key)
            password = validgetdata(request.POST.get('password'), private_key)

            try:
                user = CustomUser.objects.get(username=username, password=password)
                auth.login(request, user)
                return JsonResponse({'result': 'ok'})

            except:
                return JsonResponse({'login_error': 'Ви ввели не вірний пароль або логін'})


class EmailValidatorMixin(View):

    def accept_pin(self, request, storage_name='email_validate'):
        storage_key_in_the_database = request.GET.get('key')
        private_key = rsa_key_storage.get(str(storage_key_in_the_database))

        email = validgetdata(request.GET.get('email'), private_key)
        pin = validgetdata(request.GET.get('pin'), private_key)

        if rsa_key_storage.get(email) is None:
            return {
                'result': 'Пин код неверный'
            }
        elif pin == rsa_key_storage.get(email).decode():
            rsa_key_storage.set(email, 'ok')
            return {
                'result': 'OK'
            }
        else:
            return {
                'result': 'Пин код неверный'
            }

    def get(self, request):
        if request.is_ajax():
            return JsonResponse(self.accept_pin(request))


class SendMailPinCodeMixin(View):

    def get(self, request):
        if request.is_ajax():
            pin = self.generate_pin_code()

            storage_key_in_the_database = request.GET.get('key')

            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            email = validgetdata(request.GET.get('email'), private_key)

            if request.GET.get('restore') != None:
                try:
                    user = CustomUser.objects.get(custom_email=email)
                except:
                    return JsonResponse({'error': 'Користувача з таким email не існує'})

            self.send_validate_pin(SendMailPinCodeMixin ,request, email)
            return JsonResponse({'result': 'ok'})


    def generate_pin_code(self):
        pin_code = ''
        for i in range(5):
            pin_code += str(random.randint(0, 100))
        return pin_code

    @app.task
    def send_validate_pin(self, request, email, storage_name='email_validate'):
        mail = SendMail()
        pin = self.generate_pin_code(SendMailPinCodeMixin)
        rsa_key_storage.set(email, pin)
        rsa_key_storage.expire(email, 180)
        mail.send_mail('Код потдверждения', 'Код потдверждения {}'.format(pin), email)


class UserChangePasswordMixin(View):

    def validate_oldpassword(self, request, old_password):
        id = auth.get_user(request).id
        try:
            user = CustomUser.objects.get(id=id, password=old_password)
            return {'result': 'ok'}
        except:
            return {'password_error': 'Ви ввели не вірний пароль'}



    @method_decorator(csrf_protect)
    def post(self, request):
        if request.is_ajax():
            storage_key_in_the_database = request.POST.get('key')
            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            old_password = validgetdata(request.POST.get('old_password'), private_key)
            password1 = validgetdata(request.POST.get('new_password1'), private_key)
            password2 = validgetdata(request.POST.get('new_password2'), private_key)

            result = self.validate_oldpassword(request, old_password)
            try:
                res = result['result']
                re_p1 = re.match(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}', password1)
                re_p2 = re.match(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}', password2)

                if re_p1 == None and re_p2 == None:
                    return JsonResponse({'new_password': 'Паролі не відповідають формату'})
                elif password1 != password2:
                    return JsonResponse({'new_password': 'Паролі не співпадають'})
                else:
                    user = CustomUser.objects.filter(id=auth.get_user(request).id)[0]
                    user.password = password2
                    user.save()
                    auth.login(request, user)
                    return JsonResponse({'result': 'ok'})
            except:
                return JsonResponse(result)



class ChangePasswordMixin(View):

    def post(self, request):
        if request.is_ajax():
            data = request.POST

            storage_key_in_the_database = data.get('key')
            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            email = validgetdata(data.get('email'), private_key)
            new_password = validgetdata(data.get('password1'), private_key)
            new_password2 = validgetdata(data.get('password2'), private_key)

            if rsa_key_storage.get(email).decode() == 'ok':
                if new_password == new_password2:
                    user = CustomUser.objects.filter(custom_email=email)
                    if len(user) == 0:
                        return JsonResponse({'result': 'Користувача з таким email не існує'})
                    else:
                        user.update(password=new_password)
                        auth.login(request, user[0])

                        return JsonResponse({'result': 'ok'})
                else:
                    return JsonResponse({'result': 'Паролі не співпадають'})
            else:
                return JsonResponse({'result':  'Міша всьо хуйня'})


class AddPaymentCardMixin(View):
    def post(self, request):
        if request.is_ajax():
            data = request.POST
            storage_key_in_the_database = data.get('key')
            private_key = rsa_key_storage.get(str(storage_key_in_the_database))

            result = self.send_test(AddPaymentCardMixin ,data, private_key, request)
            if result['result'] == 'OK':
                user = CustomUser.objects.get(id=auth.get_user(request).id)

                u_card = UserCard.objects.filter(user=user)
                if len(u_card) == 0:
                    UserCard.objects.create(user=user,
                                            card_number=result['data']['card'],
                                            cvv_card=result['data']['cvv'],
                                            month_card=result['data']['mm'],
                                            year_card=result['data']['yy'],
                                            phone_number=result['data']['phone_number'])
                else:
                    u_card.update(user=user,
                                  card_number=result['data']['card'],
                                  cvv_card=result['data']['cvv'],
                                  month_card=result['data']['mm'],
                                  year_card=result['data']['yy'],
                                  phone_number=result['data']['phone_number'])
                return JsonResponse({'result': 'Карта успішно додана!'})
            else:
                return JsonResponse(result)

    @app.task
    def send_test(self, data, private_key, request):
        name_shop = auth.get_user(request).id
        user = CustomUser.objects.get(id=name_shop)

        card = validgetdata(data.get('card'), private_key)
        cvv = validgetdata(data.get('cvv'), private_key)
        mm = validgetdata(data.get('mm'), private_key)
        yy = validgetdata(data.get('yy'), private_key)
        phone = validgetdata(data.get('phone'), private_key)

        liqpay = LiqPay("sandbox_i22708126141", b"sandbox_DRE62ozXPO4UyfUU8jUGlUls2F7LV8SGussS1jxE")
        res = liqpay.api("request", {
            "action"         : "auth",
            "version"        : "3",
            "phone"          : '38'+phone,
            "amount"         : '1',
            "currency"       : 'USD',
            "description"    : 'test',
            "order_id"       : gen_link(),
            "card"           : card,
            "card_exp_month" : mm,
            "card_exp_year"  : yy,
            "card_cvv"       : cvv,
        })

        if res['result'] == 'error':
            return {'result': 'Введенні вами данні невірні'}
        else:
            if res['status'] == 'error':
                return {'result': 'Введенні вами данні невірні'}
            elif res['status'] == 'success':
                return {'result': 'OK', 'data': {
                    'phone_number': phone,
                    'card': card,
                    'cvv': cvv,
                    'yy': yy,
                    'mm': mm
                }}

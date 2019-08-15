from django.views import View
from django.contrib import auth
from django.shortcuts import render, redirect
from .models import Remittance, ChangesAwaitingConfirmation
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from UserProfile.models import CustomUser, UnreadMessage, UserCard
from Remittance.models import *
import json, redis, datetime, re, uuid, base64

key_storage = redis.Redis(host='localhost', port=6379, db=5)
asked_storage = redis.Redis(host='localhost', port=6379, db=6)

class ChatApi:

    def chats_mixin(self, request):
        id = auth.get_user(request).id

        try:
            user = CustomUser.objects.get(id=id)
            seller = Remittance.objects.filter(remittance_seller=user)
            customer = Remittance.objects.filter(remittance_customer=user)

            if len(UserCard.objects.filter(user=user)) != 0:
                return {
                    'seller_remittance': seller,
                    'customer_remittance': customer
                }
            else:
                return {
                    'card_error': 'Щоб користуватися послугами HopePay потрібно додати банківську карту в вашому профілі'
                }
        except:
            return {
                'login_error': 'Увійдіть або зареєструйтесь'
            }

    def chat_in_room(self, request, unique_link):
        id_user = auth.get_user(request).id
        try:
            user = CustomUser.objects.get(id=id_user)
        except:
            return {
                'error': 'Увійдіть або зареєструйтесь'
            }
        seller = Remittance.objects.filter(unique_link=unique_link, remittance_seller=user)
        customer = Remittance.objects.filter(unique_link=unique_link, remittance_customer=user)

        if len(seller) != 0:
            messages = seller[0].messages.all()
            return {
                'messages': messages,
                'remittance': seller[0],
                'user': user
            }
        elif len(customer) != 0:
            messages = customer[0].messages.all()
            return {
                'messages': messages,
                'remittance': customer[0],
                'user': user
            }
        else:
            return {
                'error': 'Такого договора не існує'
            }
    def ascked_test(self, request):
        try:
            user_token = str(request.COOKIES['csrftoken'])
            result = asked_storage.get(user_token)

            ascked = None

            if result != None:
                ascked = True
            else:
                ascked = False
            return ascked
        except:
            return False

class ChatsMixin(View, ChatApi):
    template = None

    def get(self, request):
        result = self.chats_mixin(request)

        ascked = self.ascked_test(request)
        try:
            customer = result['customer_remittance']
            seller = result['seller_remittance']

            user = CustomUser.objects.get(id=auth.get_user(request).id)
            unread_array = []

            for i in seller:
                unread_array.append({
                    'id': i.unique_link,
                    'unread_len': len(UnreadMessage.objects.filter(user=user, remittance=i))
                })

            for i in customer:
                unread_array.append({
                    'id': i.unique_link,
                    'unread_len': len(UnreadMessage.objects.filter(user=user, remittance=i))
                })

            return render(request, self.template, context={
                'customer': customer,
                'seller': seller,
                'ascked': ascked,
                'unreads': unread_array
            })
        except:
            try:
                login_error = result['login_error']
                return render(request, self.template, context={
                    'login_error': login_error,
                    'ascked': ascked
                })
            except:
                card_error = result['card_error']
                return render(request, self.template, context={
                    'card_error': card_error,
                    'ascked': ascked
                })

class ChatInRoomMixin(View, ChatApi):

    @method_decorator(csrf_protect)
    def post(self, request, unique_link):
        if request.is_ajax():
            user_id = auth.get_user(request).id

            unread = UnreadMessage.objects.filter(remittance=Remittance.objects.get(unique_link=unique_link),
                                                  user=CustomUser.objects.get(id=user_id))
            unread.delete()
            return JsonResponse("ok")

    def get(self, request, unique_link):
        result = self.chat_in_room(request, unique_link)

        try:
            error = result['error']
            return redirect('/not_found/')
        except:
            if request.is_ajax():
                start = int(request.GET.get('start'))
                key = request.GET.get('key')
                finish = int(request.GET.get('finish'))

                result = self.load_content(request, start, finish, result)
                try:
                    error = result['error']
                    return JsonResponse(result)
                except:
                    result = json.dumps(result)
                    pub = key_storage.get(str(key))

                    rsa = RSA.importKey(pub.decode())
                    rsa = PKCS1_v1_5.new(rsa)

                    json_result = []
                    i = 0
                    while i < len(result):
                        i += 117
                        if i >= 117:
                            append_data = rsa.encrypt(result[i-117: i].encode())
                            json_result.append(base64.b64encode(append_data).decode())

                    return JsonResponse(json.dumps(json_result), safe=False)

            else:
                seller = Remittance.objects.filter(remittance_seller=result['user'])
                customer = Remittance.objects.filter(remittance_customer=result['user'])
                ascked = self.ascked_test(request)
                unread_array = []

                for i in seller:
                    unread_array.append({
                        'id': i.unique_link,
                        'unread_len': len(UnreadMessage.objects.filter(user=result['user'], remittance=i))
                    })

                for i in customer:
                    unread_array.append({
                        'id': i.unique_link,
                        'unread_len': len(UnreadMessage.objects.filter(user=result['user'], remittance=i))
                    })
                context = {
                    'unreads': unread_array,
                    'unread_messages': UnreadMessage.objects.filter(user=CustomUser.objects.get(id=auth.get_user(request).id),
                                                                    remittance=Remittance.objects.get(unique_link=unique_link)),
                    'messages': list(result['messages'].order_by('date_created'))[-10:],
                    'seller': seller,
                    'customer': customer,
                    'ascked': ascked
                }

                user = CustomUser.objects.get(id=auth.get_user(request).id)
                try:
                    self_remittance = ChangesAwaitingConfirmation.objects.get(author=user, remittance=result['remittance'])
                except:
                    self_remittance = None
                other_remittance = None

                for i in ChangesAwaitingConfirmation.objects.filter(remittance=result['remittance']):
                    if i.author != user:
                        other_remittance = i

                fin_remittance = None
                if self_remittance == None and other_remittance == None:
                    fin_remittance = result['remittance']

                context['fin_remittance'] = fin_remittance
                context['self_remittance'] = self_remittance
                context['other_remittance'] = other_remittance
                if len(UserCard.objects.filter(user=user)) != 0:
                    return render(request, 'individual_chat.html', context=context)
                else:
                    return render(request, 'individual_chat.html', context={
                        'card_error': card_error
                    })

    def remittance_info(self, remittance, user):
        self_remittance = 'None'
        other_remittance = 'None'
        fin_remittance = 'None'
        if len(remittance.changes.all()) > 0:
            changes = ChangesAwaitingConfirmation.objects.filter(remittance=remittance)
            for i in changes:
                if i.author.id != user.id:
                    other_remittance = {
                        'unique_link': i.remittance.unique_link,
                        'changes_id': i.id,
                        'id': i.author.id,
                        'description': i.description,
                        'amount': i.amount,
                        'currency': i.currency,
                        'postal_transfer': i.postal_transfer,
                        'payment_by_installments': i.payment_by_installments,
                        'installments_count': i.installments_count,
                    }
                else:
                    self_remittance = {
                        'unique_link': i.remittance.unique_link,
                        'changes_id': i.id,
                        'id': i.author.id,
                        'description': i.description,
                        'amount': i.amount,
                        'currency': i.currency,
                        'postal_transfer': i.postal_transfer,
                        'payment_by_installments': i.payment_by_installments,
                        'installments_count': i.installments_count,
                    }
        else:
            fin_remittance = {
                'description': remittance.payment_desciption,
                'amount': remittance.amount,
                'currency': remittance.currency,
                'postal_transfer': remittance.postal_transfer,
                'paid': remittance.paid,
                'shipped': remittance.shipped,
                'successful': remittance.successful,
                'postal_code': remittance.postal_code,
                'seller_id': remittance.remittance_seller.id,
                'payment_by_installments': remittance.payment_by_installments,
                'installments_count': remittance.installments_count,
                'count_of_paid_parts': remittance.count_of_paid_parts,
            }
        return self_remittance, other_remittance, fin_remittance

    def load_content(self, request, start, finish, result):
        remittance = result['remittance']
        messages = result['messages']

        self.json_result = []
        user = CustomUser.objects.get(id=auth.get_user(request).id)
        content = list(messages.order_by('date_created'))

        pre_len = len(content)

        f_unread = 0
        len_unread_messages = 0

        for i in content:
            if len(i.unread_message.all().filter(user=user)) > 0:
                len_unread_messages += 1

        for i in content:
            message = i.unread_message.all().filter(user=user)
            if len(message) > 0:
                break
            else:
                f_unread += 1


        if len_unread_messages > 0:
            read_content = content[0: f_unread]
            if finish < 0:
                read_content = read_content[start:finish]
                content = read_content
            elif finish == 0:
                read_content = read_content[start:]

            if start < -20 and finish < 0:
                content = read_content

            elif start == -20 and finish == 0:
                unread_messages = content[f_unread: f_unread+10]
                content = read_content + unread_messages

            elif start >= 0 and finish > 0:
                unread_messages = content[f_unread:]
                content = unread_messages[start: finish]

        else:
            if finish < 0:
                content = content[start:finish]

            elif finish == 0:
                content = content[start:]

        post_len = len(content)

        if len(messages) == 0:
            pass
        elif len(content) == 0:
            return {'error': 'data already'}
        elif post_len == pre_len and start != -20 and finish != 0:
            return {'error': 'data already'}

        for i in content:
            if i.author.id == auth.get_user(request).id:
                self.json_result.append({
                    'author': i.author.username,
                    'author_photo': i.author.user_image.url,
                    'message_text': i.message_text,
                    'date_created': '{}/{} {}:{}'.format(i.date_created.day,
                                                         i.date_created.month,
                                                         i.date_created.hour,
                                                         i.date_created.minute),
                    'you_author': True
                })
            else:
                append_obj = {
                    'author': i.author.username,
                    'author_photo': i.author.user_image.url,
                    'message_text': i.message_text,
                    'date_created': '{}/{} {}:{}'.format(i.date_created.day,
                                                         i.date_created.month,
                                                         i.date_created.hour,
                                                         i.date_created.minute),
                    'you_author': False,
                    'unread': False
                }

                if len(i.unread_message.all().filter(user=user)) > 0:
                    append_obj['unread'] = True

                self.json_result.append(append_obj)

        user = CustomUser.objects.get(id=auth.get_user(request).id)
        self_remittance, other_remittance, fin_remittance = self.remittance_info(remittance, user)
        if fin_remittance != 'None':
            return {
                'fin_remittance': fin_remittance,
                'your_photo': result['user'].user_image.url,
                'first_last_name': result['user'].first_name + ' ' + result['user'].last_name,
                'id': result['user'].id,
                'messages': self.json_result
            }

        else:
            return {
                'self_remittance': self_remittance,
                'other_remittance': other_remittance,
                'your_photo': result['user'].user_image.url,
                'first_last_name': result['user'].first_name + ' ' + result['user'].last_name,
                'id': result['user'].id,
                'messages': self.json_result
            }

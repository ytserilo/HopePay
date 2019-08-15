from UserProfile.models import CustomUser, UserCard
from Remittance.models import Remittance, ChangesAwaitingConfirmation
from Chat.utils import ChatInRoomMixin
from HopePay.celery import app
from Remittance.utils import RemittanceApi
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from HopePay.aes import encrypt, decrypt
from liqpay.liqpay import LiqPay
from datetime import datetime
import json, re, uuid, requests, redis, hmac, hashlib, time, math

public_key = "sandbox_i15760037832"
private_key = b"sandbox_pHY01HT3S4gEcGtXOAJx1XKUDHZpOgtYhJNEcA6o"

key_storage = redis.Redis(host='localhost', port=6379, db=5)

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

@app.task
def check_available(postal_code, phone_number):
    apikey = '5c91a4239f54889de26a9a4a29698f16'

    request_url = "https://api.novaposhta.ua/v2.0/json/"
    json_req = {
            "apiKey": "{}".format(apikey),
            "modelName": "TrackingDocument",
            "calledMethod": "getStatusDocuments",
            "methodProperties": {
                "Documents":[
                    {
                        "DocumentNumber": "{}".format(postal_code),
                        "Phone": "{}".format(phone_number)
                    }]
            }
        }
    data = requests.post(request_url ,data=json.dumps(json_req))
    j_data = json.loads(data.content)
    status = j_data['data'][0]['StatusCode']
    return status

class RemittanceChange(RemittanceApi, ChatInRoomMixin):
    def get_customer_or_seller(self, remittance, id):
        if remittance.remittance_seller.id == id:
            return remittance.remittance_customer.id
        else:
            return remittance.remittance_seller.id

    def gen_date(self):
        now = time.time()
        last = time.ctime(now + 1209600).split(' ')

        year = last[-1]
        day = 0
        if last[2] != '':
            day = last[2]
        else:
            day = last[3]

        name = last[1].lower()
        months = {
            'jan': '01',
            'feb': '02',
            'mar': '03',
            'apr': '04',
            'may': '05',
            'jun': '06',
            'jul': '07',
            'aug': '08',
            'sep': '09',
            'oct': '10',
            'nov': '11',
            'dec': '12'
        }
        month = months[name]

        return '{}-{}-{} 00:00:00'.format(year, month, day)


    def return_data(self, self_remittance, other_remittance, fin_remittance):
        result = None

        if fin_remittance != 'None':
            result = {
                'fin_remittance': fin_remittance,
            }

        else:
            result = {
                'self_remittance': self_remittance,
                'other_remittance': other_remittance,
            }
        return json.dumps(result)


    @database_sync_to_async
    def pay(self, paid, unique_link):
        remittance = Remittance.objects.filter(unique_link=unique_link)
        date_credit = self.gen_date()

        liqpay = LiqPay(public_key, private_key)
        amount = '0'
        if remittance[0].payment_by_installments == True:
            amount = str(math.ceil(remittance[0].amount / remittance[0].installments_count))
        else:
            amount = str(remittance[0].amount)
        res = liqpay.api("request", {
            "action"         : "hold",
            "version"        : "3",
            "phone"          : '38' + paid["phone"],
            "amount"         : amount,
            "currency"       : 'UAH',
            "description"    : str(remittance[0].payment_desciption),
            "order_id"       : str(gen_link()),
            "card"           : str(paid["card"]),
            "card_exp_month" : str(paid["card_exp_month"]),
            "card_exp_year"  : str(paid["card_exp_year"]),
            "card_cvv"       : str(paid["card_cvv"]),
        })
        if res['status'] == 'hold_wait':
            remittance.update(paid=True, liqpay_order_id=res['order_id'], date_payed=str(time.time()))
            return {'pay-status': {'success': 'OK', 'user_id': remittance[0].remittance_customer.id}}
        else:
            return {'pay-status': {'error': 'Помилка платежу можливо не вірно введені дані', 'user_id': remittance[0].remittance_customer.id}}

    @database_sync_to_async
    def send_product(self, data, unique_link, user):
        remittances = Remittance.objects.filter(unique_link=unique_link)
        remittance = remittances[0]

        if remittance.shipped == True:
            return {'shipped-status': 'Ви вже відправили товар', 'user_id': user.id}
        elif remittance.paid == True and remittance.remittance_seller.id == user.id:
            if remittance.postal_transfer == True:
                postal_code = data['postal_code']
                phone_number = data['phone_number']

                status_code = check_available(postal_code, phone_number)

                if status_code == '2' or status_code == '3':
                    return {'shipped-status': {'error': 'Такої посилки немає', 'user_id': user.id}}
                else:
                    remittances.update(shipped=True, postal_code=postal_code, postal_phone=phone_number)
                    return {'shipped-status': {'success': 'Посилка відправленна', 'postal_code': postal_code, 'user_id': user.id}}
            else:
                remittances.update(shipped=True)
                return {'shipped-status': {'success': 'Посилка відправленна', 'user_id': user.id}}
        else:
            return {'shipped-status': {'error': 'Відправити товар можна тільки після оплати покупцем', 'user_id': user.id}}


    @database_sync_to_async
    def changes_awaiting_confirmation(self, data, unique_link, user):
        error_list = {}
        v_data = {
            'description': data['description'],
            'amount': data['amount'],
            'currency': data['currency'],
            'postal_transfer': data['postal_transfer'],
            'pay': data['installment']
        }

        try:
            parts = data['installments_count']
            parts = parts[parts.find('на')+3: parts.find(' місяців')]
            parts = int(parts)
        except:
            parts = ''

        result = self.validate_remittance(error_list, v_data)

        u_card_len = len(UserCard.objects.filter(user=user))
        if len(result['error_list']) > 0:
            return json.dumps(result['error_list'])
        elif len(result['error_list']) == 0 and u_card_len != 0:
            remittance = Remittance.objects.get(unique_link=unique_link)
            if remittance.paid == True:
                return json.dumps({'error': 'Не можна запропоновувати зміни в договорі коли покупець оплатив товар чи послугу', 'user_id': user.id})
            if len(ChangesAwaitingConfirmation.objects.filter(author=user, remittance=remittance)) < 1:
                ChangesAwaitingConfirmation.objects.create(remittance=remittance,
                                                           author=user,
                                                           description=data['description'],
                                                           amount=result['amount'],
                                                           currency=result['currency'],
                                                           postal_transfer=result['postal_transfer'],
                                                           payment_by_installments=result['pay'],
                                                           installments_count=result['parts'])
                self_remittance, other_remittance, fin_remittance = self.remittance_info(remittance, user)
                result = self.return_data(self_remittance, other_remittance, fin_remittance)

                return result
            else:
                changes = ChangesAwaitingConfirmation.objects.filter(remittance=remittance, author=user)
                changes.update(description=data['description'],
                               amount=result['amount'],
                               currency=result['currency'],
                               postal_transfer=result['postal_transfer'],
                               payment_by_installments=result['pay'],
                               installments_count=result['parts'])
                self_remittance, other_remittance, fin_remittance = self.remittance_info(remittance, user)
                result = self.return_data(self_remittance, other_remittance, fin_remittance)

                return result


    @database_sync_to_async
    def accept_changes_awaiting_confirmation(self, user_id, unique_link, changes_id):
        remittance = Remittance.objects.filter(unique_link=unique_link)
        changes = ChangesAwaitingConfirmation.objects.filter(id=changes_id)
        change = changes[0]

        remit = False
        try:
            user = CustomUser.objects.get(id=user_id)
            remit = Remittance.objects.get(remittance_customer=user, unique_link=unique_link)
            remit = True
        except:
            try:
                user = CustomUser.objects.get(id=user_id)
                remit = Remittance.objects.get(remittance_seller=user, unique_link=unique_link)
                remit = True
            except:
                remit = False

        if user_id != change.author.id and remit == True:
            remittance.update(postal_transfer=change.postal_transfer,
                              payment_desciption=change.description,
                              amount=change.amount,
                              currency=change.currency,
                              payment_by_installments=change.payment_by_installments,
                              installments_count=change.installments_count)
            ChangesAwaitingConfirmation.objects.filter(remittance=remittance[0]).delete()
            return json.dumps({
                'fin_remittance': {
                    'postal_transfer': change.postal_transfer,
                    'payment_desciption': change.description,
                    'amount': change.amount,
                    'currency': change.currency,
                    'seller_id': remittance[0].remittance_seller.id
                }
            })
        else:
            return "ERROR"

    def liqpay_subscribe_pay(self, remittances, mode, new_count=''):
        remittance = remittances[0]

        now = datetime.now()
        unique_id = str(gen_link())

        if mode == 'update':
            new_count = new_count['smash']
            new_count = new_count[new_count.find('на')+3: new_count.find(' місяців')]
            new_count = int(new_count)

            i_count = remittance.installments_count
            cop_parts = remittance.count_of_paid_parts
            amount = remittance.amount

            first_pay = math.ceil(amount / i_count)
            if new_count > 12 - cop_parts:
                return {'smash_data': {'error': 'error'}}
            elif new_count < 0:
                return {'smash_data': {'error': 'error'}}
            else:
                new_amount = amount - (cop_parts*first_pay)
                new_amount = math.ceil(new_amount / new_count)
                liqpay = LiqPay(public_key, private_key)
                res = liqpay.api("request", {
                    "action"        : "subscribe_update",
                    "phone"         : '38'+ str(remittance.remittance_customer.usercard.phone_number),
                    "version"       : "3",
                    "order_id"      : str(remittance.liqpay_order_id),
                    "amount"        : str(new_amount),
                    "currency"      : "UAH",
                    "description"   : remittance.payment_desciption,
                    "card"          : remittance.remittance_customer.usercard.card_number,
                    "card_exp_month": remittance.remittance_customer.usercard.month_card,
                    "card_exp_year" : remittance.remittance_customer.usercard.year_card,
                    "card_cvv"      : remittance.remittance_customer.usercard.cvv_card
                })

                if res['status'] == 'subscribed':
                    remittances.update(liqpay_order_id=res['order_id'], installments_count=cop_parts+new_count)
                    return {'smash_data': {'success': 'success'}}
                else:
                    return {'smash_data': {'error': 'error'}}
        elif mode == 'subscribe':
            if remittance.count_of_paid_parts == None:
                liqpay = LiqPay(public_key, private_key)
                res = liqpay.api("request", {
                    "action"                : "subscribe",
                    "version"               : "3",
                    "phone"                 : '38'+ str(remittance.remittance_customer.usercard.phone_number),
                    "amount"                : str(math.ceil(remittance.amount / remittance.installments_count)),
                    "currency"              : "UAH",
                    "description"           : remittance.payment_desciption,
                    "order_id"              : unique_id,
                    "subscribe"             : "1",
                    "subscribe_date_start"  : now.strftime("%Y-%m-%d %H:%M:%S"),
                    "subscribe_periodicity" : "month",
                    "card"                  : remittance.remittance_customer.usercard.card_number,
                    "card_exp_month"        : remittance.remittance_customer.usercard.month_card,
                    "card_exp_year"         : remittance.remittance_customer.usercard.year_card,
                    "card_cvv"              : remittance.remittance_customer.usercard.cvv_card
                })
                if res['status'] == 'subscribed':
                    remittances.update(liqpay_order_id=unique_id, count_of_paid_parts=1)
                    return {'smash_data': {'success': 'success'}}
                else:
                    return {'smash_data': {'error': 'error'}}
            else:
                return {'smash_data': {'error': 'error'}}

    def lipay_send(self, remittance, res='yes'):
        if res == 'yes':
            liqpay = LiqPay(public_key, private_key)
            res = liqpay.api("request", {
                "action"        : "hold_completion",
                "version"       : "3",
                "order_id"      : remittance.liqpay_order_id,
                "amount"        : str(float(remittance.amount * 0.01)),
            })

            res = liqpay.api("request", {
                "action"         : "p2p",
                "version"        : "3",
                "phone"          : '38'+remittance.remittance_customer.usercard.phone_number,
                "amount"         : remittance.amount,
                "currency"       : "UAH",
                "description"    : remittance.payment_desciption,
                "order_id"       : str(gen_link()),
                "receiver_card"  : remittance.remittance_seller.usercard.card_number,
                "card"           : remittance.remittance_customer.usercard.card_number,
                "card_exp_month" : remittance.remittance_customer.usercard.month_card,
                "card_exp_year"  : remittance.remittance_customer.usercard.year_card,
                "card_cvv"       : remittance.remittance_customer.usercard.cvv_card
            })

        else:
            liqpay = LiqPay(public_key, private_key)
            res = liqpay.api("request", {
                "action"        : "hold_completion",
                "version"       : "3",
                "order_id"      : remittance.liqpay_order_id,
                "amount"        : "1",
            })

        return res


    @database_sync_to_async
    def confirm_remittance(self, unique_link, user_id):
        remittances = Remittance.objects.filter(unique_link=unique_link)
        remittance = remittances[0]

        remit = False
        try:
            user = CustomUser.objects.get(id=user_id)
            remit = Remittance.objects.get(remittance_customer=user, unique_link=unique_link)
            remit = True
        except:
            pass

        if remittance.postal_transfer != True and remittance.shipped == True:

            if remittance.remittance_seller.id != user_id and remit == True and remittance.payment_by_installments == True:
                result = self.liqpay_subscribe_pay(remittances, 'subscribe')
                try:
                    pay_data = result['pay_data']['success']
                    return {'confirm': {'pay-success': 'OK'}}
                except:
                    pay_data = result['pay_data']['error']
                    return {'confirm': {'pay-error': 'OK'}}
            elif remittance.remittance_seller.id != user_id and remit == True:
                res = self.lipay_send(remittance)
                if res['result'] == 'ok':
                    remittances.update(successful=True, liqpay_order_id=res['order_id'])
                    return {'confirm': {'confirm-status': 'Договір успішний'}}
                else:
                    return {'confirm': {'error': 'Помилка платежу можливо не вірно введені дані'}}
            else:
                return {'confirm': {'error': 'Продавець не може підтвердити договір', 'user_id': user_id}}
        elif remittance.shipped != True:
            return {'confirm': {'error': 'Продавець ще не відправив товар', 'user_id': user_id}}
        else:
            status_code = check_available(remittance.postal_code, remittance.postal_phone)
            if status_code == '9' and remittance.paid and remittance.shipped:

                if remittance.remittance_seller.id != user_id and remit == True and remittance.payment_by_installments == True:

                    result = self.liqpay_subscribe_pay(remittances, 'subscribe')

                    try:
                        pay_data = result['pay_data']['success']
                        return {'confirm': {'pay-success': 'OK'}}
                    except:
                        pay_data = result['pay_data']['error']
                        return {'confirm': {'pay-error': 'OK'}}
                elif remittance.remittance_seller.id != user_id:
                    res = self.lipay_send(remittance)

                    if res['result'] == 'ok':

                        remittances.update(successful=True, liqpay_order_id=res['order_id'])
                        return {'confirm': {'confirm-status': 'Договір успішний'}}
                    else:
                        return {'confirm': {'error': 'Помилка платежу можливо не вірно введені дані'}}
                else:
                    return {'confirm': {'error': 'Продавець не може підтвердити договір', 'user_id': user_id}}
            else:
                return {'confirm': {'error': 'Посилка ще не дійшла', 'user_id': user_id}}

    @database_sync_to_async
    def cencell_remittance(self, unique_link, user_id):
        remittances = Remittance.objects.filter(unique_link=unique_link)
        remittance = remittances[0]

        remit = False
        try:
            user = CustomUser.objects.get(id=user_id)
            remit = Remittance.objects.get(remittance_customer=user, unique_link=unique_link)
            remit = True
        except:
            try:
                user = CustomUser.objects.get(id=user_id)
                remit = Remittance.objects.get(remittance_seller=user, unique_link=unique_link)
                remit = True
            except:
                remit = False

        if remittance.paid and remittance.shipped and remit == True:
            if remittance.postal_transfer == True:
                status = check_available(remittance.postal_code, remittance.postal_phone)
                if status == '102' or status == '103' or status == '108' or status == '106':
                    res = self.lipay_send(remittance, 'no')

                    remittances.update(successful=False, remittance_seller=None, remittance_customer=None)
                    return {'cencell': {'success': 'Ok'}}
                elif status == '9':
                    return {'cencell': {'error': 'Ви не можете відмінити платіж якщо отримали товар'}}
                else:
                    return {'cencell': {'error': 'Посилка ще не дійшла'}}
            else:
                res = self.lipay_send(remittance, 'no')

                remittances.update(successful=False, remittance_seller=None, remittance_customer=None)
                return {'cencell': {'success': 'Ok'}}

        elif remittance.paid == False and remit == True:

            remittances.update(successful=False, remittance_seller=None, remittance_customer=None)
            return {'cencell': {'success': 'Ok'}}


class RemittanceConsumer(AsyncConsumer, RemittanceChange):
    async def websocket_connect(self, event):
        url = self.scope['url_route']['kwargs']['unique_link']
        self.group_name = 'remittance_{}'.format(url)
        await self.send({
            'type': 'websocket.accept'
        })
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

    async def websocket_receive(self, event):
        url = self.scope['url_route']['kwargs']['unique_link']
        text = event.get('text')

        key = json.loads(key_storage.get(url))['decrypt_key']
        mac_key = hashlib.sha256(str(key).encode()).hexdigest()

        text = json.loads(decrypt(text.encode(), str(key)[0: 16].encode()).decode())

        self.group_name = 'remittance_{}'.format(url)
        try:
            smash = text['smash']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=smash.encode(),
                                digestmod=hashlib.sha256).hexdigest()
            if text['mac'] == conf_mac:
                smash = json.loads(decrypt(smash.encode(), str(key)[0: 16].encode()).decode())['smash']
                remittances = Remittance.objects.filter(unique_link=url)

                result = self.liqpay_subscribe_pay(remittances, 'update', smash)
                smash = encrypt(json.dumps(result), str(key)[0: 16])
                send_mac = hmac.new(key=mac_key.encode(),
                                    msg=smash,
                                    digestmod=hashlib.sha256).hexdigest()
                send_smash = {
                    'smash': smash.decode(),
                    'mac': send_mac
                }

                send_smash = encrypt(json.dumps(send_smash), str(key)[0: 16]).decode()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'show_message',
                        'text': send_smash
                    }
                )
        except:
            pass
        try:
            changes = text['changes_data']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=changes.encode(),
                                digestmod=hashlib.sha256).hexdigest()

            if text['mac'] == conf_mac:
                changes = json.loads(decrypt(changes.encode(), str(key)[0: 16].encode()).decode())['changes']

                user = CustomUser.objects.get(id=self.scope['user'].id)
                result = await self.changes_awaiting_confirmation(changes, url, user)

                try:
                    users = json.loads(key_storage.get('users'))

                    remittance = Remittance.objects.get(unique_link=url)
                    id = self.get_customer_or_seller(remittance, self.scope['user'].id)
                    index = users['{}'.format(id)]
                    try:
                        user = CustomUser.objects.get(id=id)
                        #send_mail
                    except:
                        pass
                except:
                    pass

                chgs = encrypt(json.dumps(result), str(key)[0: 16])
                send_mac = hmac.new(key=mac_key.encode(),
                                    msg=chgs,
                                    digestmod=hashlib.sha256).hexdigest()
                send_changes = {
                    'changes_data': chgs.decode(),
                    'mac': send_mac
                }

                send_changes = encrypt(json.dumps(send_changes), str(key)[0: 16]).decode()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'show_message',
                        'text': send_changes
                    }
                )

        except:
            pass
        try:
            paid = text['pay_data']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=paid.encode(),
                                digestmod=hashlib.sha256).hexdigest()
            if text['mac'] == conf_mac:
                paid = json.loads(decrypt(paid.encode(), str(key)[0: 16].encode()).decode())['pay']
                result = await self.pay(paid, url)

                try:
                    users = json.loads(key_storage.get('users'))

                    remittance = Remittance.objects.get(unique_link=url)
                    id = self.get_customer_or_seller(remittance, self.scope['user'].id)
                    index = users['{}'.format(id)]
                    try:
                        user = CustomUser.objects.get(id=id)
                        #send_mail
                    except:
                        pass
                except:
                    pass
                pd = encrypt(json.dumps(result), str(key)[0: 16].encode())

                send_mac = hmac.new(key=mac_key.encode(),
                                    msg=pd,
                                    digestmod=hashlib.sha256).hexdigest()
                send_pay = {
                    'pay_data': pd.decode(),
                    'mac': send_mac
                }

                send_pay = encrypt(json.dumps(send_pay), str(key)[0: 16].encode()).decode()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'show_message',
                        'text': send_pay
                    }
                )
        except:
            pass
        try:
            shipped = text['shipped_data']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=shipped.encode(),
                                digestmod=hashlib.sha256).hexdigest()
            if text['mac'] == conf_mac:
                shipped = json.loads(decrypt(shipped.encode(), str(key)[0: 16].encode()).decode())['shipped']
                result = await self.send_product(shipped, url, self.scope['user'])
                try:
                    users = json.loads(key_storage.get('users'))

                    remittance = Remittance.objects.get(unique_link=url)
                    id = self.get_customer_or_seller(remittance, self.scope['user'].id)
                    index = users['{}'.format(id)]
                    try:
                        user = CustomUser.objects.get(id=id)
                        #send_mail
                    except:
                        pass
                except:
                    pass
                shpd = encrypt(json.dumps(result), str(key)[0: 16])
                send_mac = hmac.new(key=mac_key.encode(),
                                    msg=shpd,
                                    digestmod=hashlib.sha256).hexdigest()
                send_shipped = {
                    'shipped_data': shpd.decode(),
                    'mac': send_mac
                }
                send_shipped = encrypt(json.dumps(send_shipped), str(key)[0: 16]).decode()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'show_message',
                        'text': send_shipped
                    }
                )
        except:
            pass
        try:
            confirm = text['confirm_data']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=confirm.encode(),
                                digestmod=hashlib.sha256).hexdigest()

            if text['mac'] == conf_mac:
                result = await self.confirm_remittance(url, self.scope['user'].id)

                try:
                    users = json.loads(key_storage.get('users'))

                    remittance = Remittance.objects.get(unique_link=url)
                    id = self.get_customer_or_seller(remittance, self.scope['user'].id)
                    index = users['{}'.format(id)]
                    try:
                        user = CustomUser.objects.get(id=id)
                        #send_mail
                    except:
                        pass
                except:
                    pass

                conf = encrypt(json.dumps(result), str(key)[0: 16])
                send_mac = hmac.new(key=mac_key.encode(),
                                    msg=conf,
                                    digestmod=hashlib.sha256).hexdigest()
                send_confirm = {
                    'confirm_data': conf.decode(),
                    'mac': send_mac
                }
                send_confirm = encrypt(json.dumps(send_confirm), str(key)[0: 16]).decode()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'show_message',
                        'text': send_confirm
                    }
                )
        except:
            pass
        try:
            cencell = text['cencell_data']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=cencell.encode(),
                                digestmod=hashlib.sha256).hexdigest()
            if text['mac'] == conf_mac:
                result = await self.cencell_remittance(url, self.scope['user'].id)
                try:
                    users = json.loads(key_storage.get('users'))

                    remittance = Remittance.objects.get(unique_link=url)
                    id = self.get_customer_or_seller(remittance, self.scope['user'].id)
                    index = users['{}'.format(id)]
                    try:
                        user = CustomUser.objects.get(id=id)
                        #send_mail
                    except:
                        pass
                except:
                    pass
                cencl = encrypt(json.dumps(result), str(key)[0: 16])
                send_mac = hmac.new(key=mac_key.encode(),
                                    msg=cencl,
                                    digestmod=hashlib.sha256).hexdigest()
                send_cencell = {
                    'cencell': cencl.decode(),
                    'mac': send_mac
                }
                send_cencell = encrypt(json.dumps(send_cencell), str(key)[0: 16]).decode()

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'show_message',
                        'text': send_cencell
                    }
                )
        except:
            pass
        try:
            accept = text['accept_data']
            conf_mac = hmac.new(key=mac_key.encode(),
                                msg=accept.encode(),
                                digestmod=hashlib.sha256).hexdigest()
            if text['mac'] == conf_mac:
                accept = json.loads(decrypt(accept, str(key)[0: 16].encode()).decode())['accept']

                user_id = self.scope['user'].id
                result = await self.accept_changes_awaiting_confirmation(user_id, url, accept['changes_id'])

                if result == 'ERROR':
                    acpt = encrypt(json.dumps({
                        'accept':
                            {
                                'error': 'Ви не можете підтвердити свою ж заміну',
                                'user_id': user_id
                            }
                        }), str(key)[0: 16])

                    send_mac = hmac.new(key=mac_key.encode(),
                                        msg=acpt,
                                        digestmod=hashlib.sha256).hexdigest()
                    send_accept = {
                        'changes_data': acpt.decode(),
                        'mac': send_mac
                    }

                    send_accept = encrypt(json.dumps(send_accept), str(key)[0: 16]).decode()
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'show_message',
                            'text': send_accept
                        }
                    )
                else:
                    try:
                        users = json.loads(key_storage.get('users'))

                        remittance = Remittance.objects.get(unique_link=url)
                        id = self.get_customer_or_seller(remittance, self.scope['user'].id)
                        index = users['{}'.format(id)]
                        try:
                            user = CustomUser.objects.get(id=id)
                            #send_mail
                        except:
                            pass
                    except:
                        pass
                    acpt = encrypt(json.dumps(result), str(key)[0: 16])

                    send_mac = hmac.new(key=mac_key.encode(),
                                        msg=acpt,
                                        digestmod=hashlib.sha256).hexdigest()
                    send_accept = {
                        'changes_data': acpt.decode(),
                        'mac': send_mac
                    }

                    send_accept = encrypt(json.dumps(send_accept), str(key)[0: 16]).decode()

                    await self.channel_layer.group_send(

                        self.group_name,
                        {
                            'type': 'show_message',
                            'text': send_accept
                        }
                    )
        except:
            pass

    async def websocket_disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def show_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

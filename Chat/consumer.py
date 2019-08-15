from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from HopePay.aes import encrypt, decrypt
from Remittance.models import Remittance

import inspect
from UserProfile.models import CustomUser, UnreadMessage
from .models import MessageChat
import json, redis, os, datetime, hashlib, re, hmac
from base64 import *


key_storage = redis.Redis(host='localhost', port=6379, db=5)


class ChatConsumer(AsyncConsumer):


    async def websocket_connect(self, event):
        room_id = self.scope['url_route']['kwargs']['unique_link']
        self.group_name = '{}'.format(room_id)

        await self.send({
            'type': 'websocket.accept'
        })
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )


    async def websocket_receive(self, event):
        room_id = self.scope['url_route']['kwargs']['unique_link']
        text = event.get('text')
        self.group_name = '{}'.format(room_id)
        try:
            text = json.loads(text)
            key = text['shared_key']

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'show_message',
                    'text': json.dumps({'shared_key': key})
                }

            )
        except:
            key = json.loads(key_storage.get(room_id))['decrypt_key']
            text = json.loads(decrypt(text.encode(), str(key)[0: 16].encode()).decode())

            mac_key = hashlib.sha256(str(key).encode()).hexdigest()

            mac_key = hmac.new(key=mac_key.encode(),
                               msg=text['message_data'].encode(),
                               digestmod=hashlib.sha256).hexdigest()
            if text['mac'] == mac_key:
                text = json.loads(decrypt(text['message_data'], str(key)[0: 16].encode()).decode())
                message = await self.create_message(text['message_text'], room_id, self.scope['user'].id)

                notification_length, friend_id = await self.notifications(room_id, text, message)
                if notification_length != None and friend_id != None:
                    try:
                        await self.channel_layer.group_send(
                                '{}'.format(friend_id),
                                {
                                    'type': 'show_message',
                                    'text': json.dumps({'length-unread-messages': notification_length, 'room_id': room_id})
                                }
                            )
                    except:
                        pass

                message_data = json.dumps({
                    'message_text': message.message_text,
                    'author_name': CustomUser.objects.get(id=self.scope['user'].id).username,
                    'author_photo': CustomUser.objects.get(id=self.scope['user'].id).user_image.url,
                    'date_created': str(message.date_created),
                    'user_id': self.scope['user'].id
                })
                message_data = encrypt(message_data, str(key)[0: 16])
                send_key = hmac.new(key=hashlib.sha256(str(key).encode()).hexdigest().encode(),
                                    msg=message_data,
                                    digestmod=hashlib.sha256).hexdigest()

                send_data = {
                    'message_data': message_data.decode(),
                    'mac': send_key
                }

                send_data = encrypt(json.dumps(send_data), str(key)[0: 16])

                await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'show_message',
                            'text': send_data.decode()
                        }
                    )



    async def websocket_disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    @database_sync_to_async
    def notifications(self, room_id, text, message):
        friend_id = None
        try:
            remittance = Remittance.objects.get(unique_link=room_id, remittance_customer=self.scope['user'])

            friend_id = remittance.remittance_seller.id
        except:
            pass
        try:
            remittance = Remittance.objects.get(unique_link=room_id, remittance_seller=self.scope['user'])

            friend_id = remittance.remittance_customer.id
        except:
            pass
        try:
            friend = CustomUser.objects.get(id=friend_id)
            remittance = Remittance.objects.get(unique_link=room_id)


            UnreadMessage.objects.create(user=friend,
                                         remittance=remittance,
                                         message=message,
                                         date_created=datetime.datetime.now())
            notification_length = len(UnreadMessage.objects.filter(user=friend, remittance=remittance))

            return notification_length, friend_id
        except:
            return None, None

    @database_sync_to_async
    def create_message(self, message_text, room_id, user_id):
        remittance = Remittance.objects.filter(unique_link=room_id)[0]

        remittance.last_event=datetime.datetime.now()
        remittance.save()
        author = CustomUser.objects.get(id=user_id)


        return MessageChat.objects.create(remittance=remittance,
                                             author=author,
                                             message_text=message_text,
                                             date_created=datetime.datetime.now())


    async def show_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

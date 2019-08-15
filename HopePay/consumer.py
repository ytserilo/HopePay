from channels.consumer import AsyncConsumer
from UserProfile.models import CustomUser
from Remittance.models import Remittance
import json, redis

key_storage = redis.Redis(host='localhost', port=6379, db=5)

class UserStatus(AsyncConsumer):

    async def websocket_connect(self, event):
        user_id = self.scope['user'].id

        await self.send({
            'type': 'websocket.accept'
        })
        await self.channel_layer.group_add(
            '{}'.format(user_id),
            self.channel_name
        )


    async def websocket_receive(self, event):
        text = json.loads(event.get('text'))
        user_id = self.scope['user'].id

        user_status = ['online', 'offline', 'away', 'busy']
        status = text['status']

        if status in user_status:
            friends_array = self.change_status(user_id, status)
            for i in friends_array:
                try:
                    await self.channel_layer.group_send(
                        '{}'.format(i.id),
                        {
                            "type": "show_message",
                            "text": json.dumps({
                                'status': status,
                                'id': str(user_id)
                            })
                        }
                    )
                except:
                    pass


    def change_status(self, user_id, status):
        user = CustomUser.objects.filter(id=user_id)
        user.update(status=status)

        friends_array = []
        for i in Remittance.objects.filter(remittance_seller=user[0]):
            if i.successful != True and i.successful != False:
                if i.remittance_customer not in friends_array:
                    friends_array.append(i.remittance_customer)
        for i in Remittance.objects.filter(remittance_customer=user[0]):
            if i.successful != True and i.successful != False:
                if i.remittance_seller not in friends_array:
                    friends_array.append(i.remittance_seller)

        return friends_array


    async def websocket_disconnect(self, close_code):
        user_id = self.scope['user'].id
        friends_array = self.change_status(user_id, 'offline')

        users = json.loads(key_storage.get('users'))
        try:
            last = users.pop('{}'.format(user_id))
            key_storage.set('users', json.dumps(users))

        except:
            pass
        for i in friends_array:
            try:
                await self.channel_layer.group_send(
                    '{}'.format(i.id),
                    {
                        "type": "show_message",
                        "text": json.dumps({
                            'status': 'offline',
                            'id': str(user_id)
                        }),
                    }
                )
            except:
                pass
        await self.channel_layer.group_discard(
            '{}'.format(user_id),
            self.channel_name
        )

    async def show_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

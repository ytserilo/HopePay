from channels.consumer import AsyncConsumer
from Remittance.models import ChangesAwaitingConfirmation
from Remittance.utils import RemittanceApi
from UserProfile.models import CustomUser
from HopePay.celery import app
from UserProfile.send_mail import SendMail
from channels.db import database_sync_to_async
from .models import Product
import json

class AuctionConsumer(AsyncConsumer, RemittanceApi):
    async def websocket_connect(self, event):
        product_id = self.scope['url_route']['kwargs']['id']
        self.group_id = '{}'.format(product_id)

        await self.send({
            'type': 'websocket.accept'
        })
        await self.channel_layer.group_add(
            self.group_id,
            self.channel_name
        )

    async def websocket_receive(self, event):
        product_id = self.scope['url_route']['kwargs']['id']
        self.group_id = '{}'.format(product_id)

        data = json.loads(event.get('text'))
        result = await self.create_rate(self.scope['user'].id, self.group_id, data)
        if result != None:
            await self.channel_layer.group_send(
                self.group_id,
                {
                    "type": "show_message",
                    "text": json.dumps({
                        "amount": result[1].amount,
                        "id": result[1].id,
                        "author": {
                            "id": result[0].id,
                            "img": result[0].user_image.url,
                            "name": result[0].first_name + ' ' + result[0].last_name,
                        }
                    })
                }
            )
            #send mail notification

    @database_sync_to_async
    def create_rate(self, author_id, product_id, data):
        author = CustomUser.objects.get(id=author_id)
        product = Product.objects.get(id=product_id)

        result = self.validate_remittance({}, data)

        if len(result['error_list']) == 0:
            if author != product.author:
                rate = ChangesAwaitingConfirmation.objects.filter(author=author, product=product)
                if len(rate) > 0:
                    rate.update(description=data['description'],
                                amount=result['amount'],
                                currency=result['currency'],
                                payment_by_installments=result['pay'],
                                installments_count=result['parts'])
                    rate = rate[0]
                else:
                    rate = ChangesAwaitingConfirmation.objects.create(author=author,
                                                                      product=product,
                                                                      description=data['description'],
                                                                      amount=result['amount'],
                                                                      currency=result['currency'],
                                                                      payment_by_installments=result['pay'],
                                                                      installments_count=result['parts'])
                return [author, rate]
            else:
                return None
        else:
            return None

    async def show_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    async def websocket_disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_id,
            self.channel_name
        )

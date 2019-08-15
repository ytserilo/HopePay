from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from HopePay.aes import encrypt, decrypt

user_storage = redis.Redis(host='localhost', port=6379, db=5)


class HopeCoinConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user_id = self.scope['user'].id
        self.group_name = 'hp_user_'+str(user_id)

        problem = user_storage.get('problem')
        if problem == None:
            problem = {
                'problem': 'new',
            }
            user_storage.set('problem', json.dumps(problem))

        hp_users = user_storage.get('hopecoins')
        users = user_storage.get('queue_users')

        if hp_users == None:
            data = {
                '{}'.format(user_id): 0
            }
            user_storage.set('hopecoins', json.dumps(data))
        else:
            try:
                user_coins = hp_users['{}'.format(user_id)]
            except:
                hp_users['{}'.format(user_id)] = 0
                user_storage.set('hopecoins', json.dumps(hp_users))
        if users == None:
            data = {
                '{}'.format(user_id): {
                    'encdec_key': self.scope['cookies']['csrftoken']
                }
            }
            user_storage.set('queue_users', json.dumps(data))
        else:
            users['{}'.format(user_id)] = {
                'encdec_key': self.scope['cookies']['csrftoken']
            }
            user_storage.set('queue_users', json.dumps(users))

        if len(json.loads(user_storage.get('queue_users'))) == 1:
            send_block = ''
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'show_message',
                    'text': send_block.decode()
                }
            )

        await self.send({
            'type': 'websocket.accept'
        })
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

    @database_sync_to_async
    def add_coins(self, hash, remittance):
        queue = json.loads(user_storage.get('queue_users'))
        all_count = 0
        price_of_one = 15 / all_count

        for i in list(queue):
            all_count += queue[i]

        for i in list(queue):
            count = queue[i]
            hp = HopeCoin.objects.filter(user=CustomUser.objects.get(id=i))
            coins = hp[0].count_coins + (count * price_of_one)
            hp.update(count_coins=coins)
            queue[i] = 0

        user_storage.set('queue_users', json.dumps(queue))
        OrderItem.objects.create(orderitem_seller=remittance.remittance_seller,
                                 orderitem_customer=remittance.remittance_customer,
                                 payment_description=remittance.payment_desciption,
                                 amount=remittance.amount,
                                 currency=remittance.currency,
                                 hash=hash)

    @database_sync_to_async
    def block(self, remittance, order=False, hash):
        data = {}
        if order == False:
            data = {
                'seller': remittance.remittance_seller,
                'customer': remittance.remittance_customer,
                'description': remittance.payment_desciption,
                'amount': remittance.amount,
                'currency': remittance.currency,
                'hash': hash
            }
        else:
            data = {
                'seller': order.orderitem_seller,
                'customer': order.orderitem_customer,
                'description': order.payment_description,
                'amount': order.amount,
                'currency': order.currency,
                'hash': hash
            }
        return json.dumps(hashlib.sha256(data.encode()).hexdigest())

    async def websocket_receive(self, event):
        user_id = self.scope['user'].id
        data = event.get('text')

        queue = json.loads(user_storage.get('queue_users'))

        key = queue[str(user_id)]['encdec_key']
        data = json.loads(encrypt(data))

        problem = json.loads(user_storage.get('problem'))

        queue_list = list(queue)
        queue[queue_list[0]] = queue.pop(queue_list[0])
        user_storage.set('queue_users', json.dumps(queue))

        if problem['problem'] == 'new':
            if data['status'] == 'success':
                hp = user_storage.get('hopecoins')
                hp['{}'.format(user_id)] += data['count']
                user_storage.set('hopecoins', json.dumps(hp))

                user_storage.set('problem', json.dumps({'problem': 'prepare', 'counter': 1}))

                remittances = Remittance.objects.filter(successful=True)
                await self.add_coins(hash=data['hash'], remittance=remittances[0])
                remittances[0].delete()

                orders = OrderItem.objects.all()
                send_block = self.block(order=order[1], hash=orders[0].hash)

                await self.channel_layer.group_send(
                    'hp_user_'+ list(json.loads(user_storage.get('queue_users')))[0],
                    {
                        'type': 'show_message',
                        'text': send_block.decode()
                    }
                )
            else:
                hp = user_storage.get('hopecoins')
                hp['{}'.format(user_id)] += data['count']
                user_storage.set('hopecoins', hp)

                await self.channel_layer.group_send(
                    'hp_user_'+ list(json.loads(user_storage.get('queue_users')))[0],
                    {
                        'type': 'show_message',
                        'text': data['hash']
                    }
                )
        else:
            if data['status'] == 'success':
                count = problem['counter']
                orders = OrderItem.objects.all()
                remittances = Remittance.objects.filter(successful=True)
                if data['hash'] == orders[count-1].hash:
                    send_block = None

                    if len(orders) == count+1 and len(remittances) != 0:
                        user_storage.set('problem', json.dumps({'problem': 'new'}))
                        send_block = self.block(remittance=remittances[0], hash=orders[-1].hash)

                    elif len(orders) == count+1 and len(remittances) == 0:
                        pass

                    else:
                        user_storage.set('problem', json.dumps({'problem': 'prepare', 'counter': count+1}))
                        send_block = self.block(order=orders[count+1], hash=orders[count].hash)

                    await self.channel_layer.group_send(
                        'hp_user_'+ list(json.loads(user_storage.get('queue_users')))[0],
                        {
                            'type': 'show_message',
                            'text': send_block.decode()
                        }
                    )
                else:
                    #backup
                    pass

            else:
                hp = user_storage.get('hopecoins')
                hp['{}'.format(user_id)] += data['count']
                user_storage.set('hopecoins', hp)

                await self.channel_layer.group_send(
                    'hp_user_'+ list(json.loads(user_storage.get('queue_users')))[0],
                    {
                        'type': 'show_message',
                        'text': data['hash']
                    }
                )


    async def websocket_disconnect(self, code):
        pass

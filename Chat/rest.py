class ChatInRoomApi(ApiView, ChatApi):
    def get(self, request, format=None):
        result = self.chats_mixin(request)
        try:
            customer = result['customer_remittance']
            seller = result['seller_remittance']

            seller_serializer = MessageSerializer(seller, many=True)
            customer_serializer = MessageSerializer(customer, many=True)
            return Response(seller_serializer.data, customer_serializer.data)
        except:
            return Response(json.dump(result))


class ChatsApi(ApiView, ChatApi):
    def get(self, request, id, format=None):
        result = self.chat_in_room(request, id)
        try:
            seller = result['seller']
            messages = result['messages']

            seller_serializer = MessageSerializer(seller, many=True)
            messages_serializer = MessageSerializer(messages, many=True)
            return Response(seller_serializer.data, messages_serializer.data)
        except:
            pass

        try:
            customer = result['customer']
            messages = result['messages']

            customer_serializer = MessageSerializer(customer, many=True)
            messages_serializer = MessageSerializer(messages, many=True)
            return Response(customer_serializer.data, messages_serializer.data)
        except:
            pass

        try:
            return Response(json.dump(result))
        except:
            pass

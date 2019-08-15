from django.views import View
from django.contrib import auth
from django.http import JsonResponse, HttpResponse
from UserProfile.models import CustomUser
import os, redis, json

key_storage = redis.Redis(host='localhost', port=6379, db=5)

class DH(View):
    def get(self, request):
        if request.is_ajax():
            data = request.GET

            id = str(data.get('id'))
            user_id = str(auth.get_user(request).id)

            user_secret_key = int(''.join([str(ord(i)) for i in str(request.COOKIES['csrftoken'])])[:4])

            data = key_storage.get(id)
            
            if data != None:
                data = json.loads(data)
                users = data['users']
                if len(users) > 1:
                    if users[user_id]['secret_key'] == user_secret_key:
                        result = self.send_key(users, data, user_id)
                        return JsonResponse(result)
                    else:
                        result = self.update_key(users, data, id, user_id, user_secret_key)
                        return JsonResponse(result)
                else:
                    try:
                        user = users[user_id]
                        result = self.send_or_update_key(data, user_secret_key, user_id, id)
                        return JsonResponse(result)
                    except:
                        result = self.add_new_user(data, user_secret_key, user_id, id)
                        return JsonResponse(result)
            else:
                result = self.create_first_keys(user_secret_key, user_id, id)
                return JsonResponse(result)

    def update_key(self, users, data, id, user_id, user_secret_key):
        data['users'][user_id]['secret_key'] = user_secret_key

        users_keys = users.keys()
        other_key = None
        self_key = None

        for i in users_keys:
            if i != user_id:
                other_key = users[i]['secret_key']
            else:
                self_key = users[i]['secret_key']

        self_shared_key = data['server_shared_key']**other_key % data['p']
        other_shared_key = data['server_shared_key']**self_key % data['p']

        data['decrypt_key'] = other_shared_key**other_key % data['p']

        key_storage.set(id, json.dumps(data))
        return {
            'update_key': {
                'self_key': str(self_shared_key),
                'key_for_other': str(other_shared_key),
                'p': str(data['p'])
            }
        }


    def send_key(self, users, data, user_id):
        users_keys = users.keys()
        key = None

        for i in users_keys:
            if i != user_id:
                key = users[i]['secret_key']

        self_shared_key = data['server_shared_key']**key % data['p']

        return {
            'shared_key': str(self_shared_key),
            'p': str(data['p'])
        }

    def add_new_user(self, data, user_secret_key, user_id, id):
        user_shared_key = data['g']**user_secret_key % data['p']
        data['users'][user_id] = {'secret_key': user_secret_key}

        users_keys = data['users'].keys()
        key = None
        for i in users_keys:
            if i != user_id:
                key = data['users'][i]['secret_key']
        self_shared_key = data['decrypt_key']

        data['decrypt_key'] = data['decrypt_key']**user_secret_key % data['p']

        key_storage.set(id, json.dumps(data))

        return {
            'update_key': {
                'self_key': str(self_shared_key),
                'key_for_other': str(data['server_shared_key']**user_secret_key % data['p']),
                'p': str(data['p'])
            }
        }


    def send_or_update_key(self, data, user_secret_key, user_id, id):
        if data['users'][user_id]['secret_key'] == user_secret_key:

            return {
                'shared_key': str(data['server_shared_key']),
                'p': str(data['p'])
            }
        else:
            data['users'][user_id]['secret_key'] = user_secret_key

            data['decrypt_key'] = data['server_shared_key']**user_secret_key % data['p']
            data['users'][user_id]['shared_key'] = data['g']**user_secret_key % data['p']

            key_storage.set(id, json.dumps(data))

            return {
                'update_key': {
                    'shared_key': str(data['server_shared_key']),
                    'p': str(data['p'])
                }

            }

    def create_first_keys(self, user_secret_key, user_id, id):
        p = int(''.join([str(i) for i in os.urandom(16)]))
        g = int(''.join([str(i) for i in os.urandom(4)])[:4])
        server_secret_key = int(''.join([str(i) for i in os.urandom(4)])[:4])

        server_shared_key = g**server_secret_key % p

        user_shared_key = g**user_secret_key % p

        decrypt_key = user_shared_key**server_secret_key % p
        key_storage.set(id, json.dumps({
            'p': p,
            'g': g,
            'server_secret_key': server_secret_key,
            'server_shared_key': server_shared_key,
            'decrypt_key': decrypt_key,
            'users': {
                user_id: {'secret_key': user_secret_key}
            }
        }))

        return {
            'p': str(p),
            'shared_key': str(server_shared_key)
        }

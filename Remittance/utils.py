from django.views import View
from django.contrib import auth
from liqpay.liqpay import LiqPay
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Remittance, ChangesAwaitingConfirmation
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from UserProfile.models import CustomUser, UserCard
import redis, json, uuid, hashlib, random, re
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import *
from channels.db import database_sync_to_async
import asyncio, aiohttp

r = redis.Redis(host='localhost', port=6379, db=2)
rsa_key_storage = redis.Redis(host='localhost', port=6379, db=5)

def validate_get_data(text, key):
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

class RemittanceApi:
    def validate_remittance(self, error_list, data):
        amount = data['amount']
        pay = data['pay']
        try:
            parts = data['parts']
        except:
            pass

        if str(pay).lower() == 'true':
            pay = True
        else:
            pay = False

        try:
            parts = int(parts)
            if parts > 12:
                parts = 12
            elif parts < 2:
                parts = 2
            else:
                parts = parts
        except:
            if pay == True:
                parts = 2
            else:
                parts = None
        args = {
            'parts': parts,
            'pay': pay,
            'postal_transfer': True,
            'currency': 'UAH',
            'amount': amount,
            'error_list': error_list
        }
        try:
            seller = data['seller']
            if str(seller).lower() == 'true':
                seller = True
            else:
                seller = False
            args['seller'] = seller
        except:
            pass

        return args

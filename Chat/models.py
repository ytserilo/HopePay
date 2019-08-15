# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Remittance.models import *
import redis, uuid, datetime, hashlib, json, os
# db = 0 is message DataBase
message_blockchain = redis.Redis(host='localhost', port=6379, db=0)


class MessageChat(models.Model):
    remittance = models.ForeignKey('Remittance.Remittance',
                                   on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey('UserProfile.CustomUser',
                               on_delete=models.CASCADE)
    message_text = models.TextField()
    photo_message = models.ImageField(upload_to='message_image/', blank=True)
    record_voice = models.FileField(upload_to='message_voice/', blank=True)
    read_status = models.BooleanField(blank=True, null=True)
    date_created = models.DateTimeField()

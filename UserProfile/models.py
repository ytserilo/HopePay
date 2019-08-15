# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from Chat.models import *


class CustomUser(User):
    STATUS_CHOICE = (
        ('online', 'online'),
        ('offline', 'offline'),
        ('busy', 'busy'),
        ('away', 'away')
    )
    custom_email = models.EmailField(blank=True, verbose_name='email', unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует',
        })
    user_image = models.ImageField(upload_to='user_image/', default='user_image/default.png')

    status = models.CharField(max_length=25, choices=STATUS_CHOICE, default='online')


class UnreadMessage(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='user_unread')
    remittance = models.ForeignKey('Remittance.Remittance', on_delete=models.CASCADE, related_name='unread_remittance')
    message = models.ForeignKey('Chat.MessageChat', on_delete=models.CASCADE, related_name='unread_message')

class UserCard(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='usercard')
    card_number = models.CharField(max_length=20)
    cvv_card = models.CharField(max_length=3)
    month_card = models.CharField(max_length=2)
    year_card = models.CharField(max_length=2)
    phone_number = models.CharField(max_length=10, blank=True)

import redis, re, smtplib, random, uuid, os, datetime, json, hashlib
from django.db import models

# db=1 Order DataBase
order_blockchain = redis.Redis(host='localhost', port=6379, db=1)


class Remittance(models.Model):
    unique_link = models.CharField(max_length=32)
    product = models.ForeignKey('market.Product', blank=True,
                                null=True, on_delete=models.CASCADE,
                                related_name='product_remittance')
    remittance_seller = models.ForeignKey('UserProfile.CustomUser',
                                  verbose_name='Продавець',
                                  blank=True, null=True,
                                  on_delete=models.CASCADE,
                                  related_name='remittance_seller')

    remittance_customer = models.ForeignKey('UserProfile.CustomUser',
                                    verbose_name='Покупатель',
                                    blank=True, null=True,
                                    on_delete=models.CASCADE,
                                    related_name='remittance_customer')

    postal_code = models.CharField(max_length=255,
                                   verbose_name='Номер накладної', blank=True)
    postal_transfer = models.BooleanField(blank=True)

    paid = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    postal_phone = models.CharField(max_length=12, blank=True)

    successful = models.BooleanField(blank=True, null=True)

    date_payed = models.CharField(max_length=255, blank=True)

    amount = models.IntegerField(verbose_name='Сума')
    currency = models.CharField(max_length=5, verbose_name='Валюта')
    payment_desciption = models.TextField()

    payment_by_installments = models.BooleanField(blank=True, null=True)
    installments_count = models.IntegerField(blank=True, null=True)
    count_of_paid_parts = models.IntegerField(blank=True, null=True)

    liqpay_order_id = models.CharField(max_length=512, blank=True)


class ChangesAwaitingConfirmation(models.Model):
    product = models.ForeignKey('market.Product', on_delete=models.CASCADE, related_name='product_changes', blank=True, null=True)
    remittance = models.ForeignKey(Remittance, on_delete=models.CASCADE, related_name="changes", blank=True, null=True)
    author = models.ForeignKey('UserProfile.CustomUser', on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.IntegerField()
    currency = models.CharField(max_length=5, verbose_name='Валюта')
    postal_transfer = models.BooleanField(blank=True, null=True)
    payment_by_installments = models.BooleanField(blank=True, null=True)
    installments_count = models.IntegerField(blank=True, null=True)

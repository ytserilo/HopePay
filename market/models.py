from django.db import models
from datetime import datetime

class Product(models.Model):
    author = models.ForeignKey('UserProfile.CustomUser',
                               on_delete=models.CASCADE,
                               related_name='author_product',
                               blank=True, null=True)

    title = models.CharField(max_length=255, default="Заголовок")
    location = models.CharField(max_length=512, default="Місце")
    description = models.TextField()

    amount = models.IntegerField(verbose_name='Сума')
    currency = models.CharField(max_length=5, verbose_name='Валюта')
    payment_desciption = models.TextField()

    payment_by_installments = models.BooleanField(blank=True, null=True)
    installments_count = models.IntegerField(blank=True, null=True)

    postal_transfer = models.BooleanField(blank=True)
    active_status = models.BooleanField(default=True)
    seller = models.BooleanField()

class Images(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='images')
    img = models.ImageField(upload_to='product_images/')

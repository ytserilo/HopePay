from django.db import models
from UserProfile.models import CustomUser
from Remittance.models import Remittance
# Create your models here.

class HopeCoin(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    count_coins = models.FloatField()

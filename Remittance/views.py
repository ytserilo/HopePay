
from django.http import JsonResponse
from django.views import View
from market.models import Product
from UserProfile.models import CustomUser
from django.contrib import auth
from .utils import *

public_key = "sandbox_i15760037832"
private_key = b"sandbox_pHY01HT3S4gEcGtXOAJx1XKUDHZpOgtYhJNEcA6o"


class Orders(View):
    def get(self, request):
        products = Product.objects.filter(author=CustomUser.objects.get(id=auth.get_user(request).id))

        return render(request, 'orders.html', context={
            'orders_seller': products.filter(seller=True),
            'orders_customer': products.filter(seller=False),
        })

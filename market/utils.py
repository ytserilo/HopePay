import json, os, re
import ast
from django.views import View
from django.http import JsonResponse, HttpResponse
from .models import Product
from django.shortcuts import render, redirect
from django.contrib import auth
from django.core.paginator import Paginator
from HopePay.aes import encrypt, decrypt
from Remittance.utils import RemittanceApi, validate_get_data
from UserProfile.models import *

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


class AboutProductMixin(View):
    def like_products(self, obj, main, sub):
        append_dict = {}
        if main in obj.description :
            append_dict = {
                'price': obj.amount,
                'title': obj.title,
                'parts': obj.installments_count,
                'id': obj.id
            }
            if len(obj.images.all()) > 0:
                append_dict['image'] = [i.url for i in obj.images.all()][0]
        if len(append_dict) > 0:
            return append_dict
        else:
            return None

    def get(self, request, id):
        product = Product.objects.get(id=id)
        user = CustomUser.objects.get(id=auth.get_user(request).id)

        detail_data = ast.literal_eval(product.description)
        json_description = None
        like_products_seller = []
        like_products_customer = []

        for main in detail_data:
            for sub in detail_data[main]:
                seller = Product.objects.filter(author=product.author, seller=True).exclude(id=id)
                customer = Product.objects.filter(author=product.author, seller=False).exclude(id=id)

                for i in range(4):
                    try:
                        seller_prd = seller[i]
                        result = self.like_products(seller_prd, main, sub)
                        if result != None:
                            like_products_seller.append(result)
                    except:
                        continue
                    try:
                        customer_prd = customer[i]
                        result = self.like_products(customer_prd, main, sub)
                        if result != None:
                            like_products_customer.append(result)
                    except:
                        continue

                for und in detail_data[main][sub]:
                    if len(und) == 1:
                        json_description = detail_data[main][sub][und]
                    else:
                        json_description = detail_data[main][sub]

        rates = []

        for i in list(product.product_changes.exclude(author=product.author).order_by('-amount'))[:7]:
            rates.append({
                'amount': i.amount,
                'author-name': i.author.first_name + ' ' + i.author.last_name,
                'author-photo': i.author.user_image.url,
                'parts': i.installments_count,
                'id': i.id,
            })

        if request.is_ajax():
            data = {
                'title': product.title,
                'price': product.amount,
                'description': product.payment_desciption,
                'json-data': json_description,
                'images': [i.url for i in product.images.all()],
                'location': product.location,
                'rates': rates,
                'like_products_seller': like_products_seller,
                'like_products_customer': like_products_customer,
            }
            return JsonResponse({'data': json.dumps(data)})
        else:
            return render(request, 'product.html', context={
                'product': product
            })

class AddProductMixin(View, RemittanceApi):
    def get(self, request):
        return render(request, 'add_product.html')

    def post(self, request):
        if request.is_ajax():
            data = request.POST.get('data')
            data = json.loads(decrypt(data, request.COOKIES['csrftoken'][0:16]))
            user_id = auth.get_user(request).id
            args = {}
            try:
                cards = UserCard.objects.filter(user=CustomUser.objects.get(id=user_id))
                if len(cards) == 0:
                    args['card_error'] = 'Щоб користуватися послугами HopePay потрібно додати банківську карту в вашому профілі'
            except:
                args['login_error'] = 'Увійдіть або Зареєструйтесь'

            if len(args) == 0:
                error_list = self.validate_data(data['category-data'])

                if len(error_list) == 0:
                    result = self.create_remitance(data, user_id, data['category-data'])
                    try:
                        result = result['error_list']
                        return JsonResponse(result)
                    except:
                        return JsonResponse({'result': 'success'})
                else:
                    return JsonResponse(error_list)
            else:
                return JsonResponse(args)
        else:
            return HttpResponse('Error')

    def create_remitance(self, data, user_id, product_data):
        error_list = {}
        try:
            user = CustomUser.objects.get(id=user_id)
        except:
            error_list['login_error'] = 'Войдите или зарагестрируйтесь'

        result = self.validate_remittance(error_list, data)
        u_card_len = len(UserCard.objects.filter(user=user))
        if len(result['error_list']) == 0 and data['description'] != '' and result['amount'] != '' and result['currency'] != '' and result['postal_transfer'] != '' and result['seller'] != '' and u_card_len != 0:

            if data['seller']:
                product = Product.objects.create(author=user, payment_desciption=data['description'],
                                                 amount=result['amount'], currency=result['currency'],
                                                 payment_by_installments=result['pay'], installments_count=result['parts'],
                                                 postal_transfer=result['postal_transfer'], seller=True,
                                                 title=data['title'], location=data['location'], description=product_data)
                return product

            else:
                product = Product.objects.create(author=user, payment_desciption=data['description'],
                                                 amount=result['amount'], currency=result['currency'],
                                                 payment_by_installments=result['pay'], installments_count=result['parts'],
                                                 postal_transfer=result['postal_transfer'], seller=False,
                                                 title=data['title'], location=data['location'], description=product_data)
                return product
        else:
            return result['error_list']

    def validate_data(self, input_data, page=None, mode='validation', view_mode='seller'):
        with open('market/static/json/categories.json', 'r') as file:
            data = json.loads(file.read())

        if mode == 'filter':
            products = []
            if view_mode == 'seller':
                products = list(Product.objects.filter(seller=False, active_status=True))
            elif view_mode == 'customer':
                products = list(Product.objects.filter(seller=True, active_status=True))

        error_list = {}

        try:
            key = [i for i in input_data]
            if mode == 'filter':
                if 'Оберіть рубрику' in key[0]:
                    pass
                else:
                    products = self.fast_filter(products, key[0])
            elif mode == 'validation':
                check_data = data[key[0]]
                inp_data = input_data[key[0]]
        except:
            error_list['main-category-error'] = 'Такої категорії не існує'
        try:
            key = [i for i in input_data]
            sub_key = [i for i in input_data[key[0]]]
            und_cat = None

            if mode == 'filter':
                try:
                    check_data = data[key[0]][sub_key[0]]
                    inp_data = input_data[key[0]][sub_key[0]]
                except:
                    try:
                        check_data = data[key[0]]
                        inp_data = input_data[key[0]]
                    except:
                        check_data = data
                        inp_data = input_data
                try:
                    try_sub = sub_key[0]
                    if 'Оберіть категорію' in sub_key[0] or len(sub_key) > 1:
                        pass
                    else:
                        products = self.fast_filter(products, sub_key[0])
                except:
                    pass

            else:
                check_data = data[key[0]][sub_key[0]]
                inp_data = input_data[key[0]][sub_key[0]]
                try:
                    sub_cat = check_data['sub-category']

                    try:
                        und_cat = [i for i in input_data[key[0]][sub_key[0]]]
                        check_data = check_data[und_cat[0]]
                        inp_data = input_data[key[0]][sub_key[0]][und_cat[0]]

                        if mode == 'filter':
                            products = self.fast_filter(products, und_cat[0])
                    except:
                        error_list['und-category-error'] = 'Такої категорії не існує'
                except:
                    pass
        except:
            error_list['sub-category-error'] = 'Такої категорії не існує'

        if len(error_list) == 0:
            switch = None
            for category in inp_data:
                category = category.replace('-min', '')
                category = category.replace('-max', '')

                try:
                    criterias = check_data[category]
                except:
                    pass

                if 'brand-select' in category:
                    if inp_data['Модель select'] not in check_data[category][inp_data['Марка brand-select']]:
                        error_list['model-error'] = 'Такої моделі не існує'
                    if mode == 'filter':
                        brand_products = self.fast_filter(products, inp_data['Марка brand-select'])
                        products = self.fast_filter(brand_products, inp_data['Модель select'])

                elif 'Модель' in category:
                    continue

                elif 'number' in category:
                    if mode == 'filter':
                        if switch != category:
                            ctg = category.replace('-min', '')
                            ctg = category.replace('-max', '')

                            if und_cat != None:
                                products = self.fast_filter(products, [[key[0], sub_key[0], und_cat[0]], inp_data, ctg], 'number')
                            else:
                                products = self.fast_filter(products, [[key[0], sub_key[0]], inp_data, ctg], 'number')
                            switch = category
                    else:
                        min = int(criterias['min'])
                        max = int(criterias['max'])
                        try:
                            number = int(inp_data[category])
                            if number > max:
                                error_list[category+'-error'] = 'Значення повинне бути менше {}'.format(max)
                            elif number < min:
                                error_list[category+'-error'] = 'Значення повинне бути більше {}'.format(min)
                        except:
                            error_list[category+'-error'] = 'Це поле не може бути пустим'

                elif 'checkbox' in category:
                    for i in inp_data[category]:
                        if i not in criterias:
                            error_list[category+'-error'] = 'Такої критерії не існує'
                        else:
                            if mode == 'filter':
                                products = self.fast_filter(products, i)

                elif 'select' in category:
                    select_list = [i for i in criterias]
                    if inp_data[category] not in select_list:
                        error_list[category+'-error'] = 'Такої критерії не існує'
                    if mode == 'filter':
                        products = self.fast_filter(products, inp_data[category])


            if mode == 'filter':
                if len(sub_key) == 0:
                    product_category = key[0]
                elif und_cat == None:
                    product_category = key[0]+' /'+sub_key[0]
                else:
                    product_category = key[0]+' /'+sub_key[0]+' /'+und_cat[0]
                paginator = self.valid_paginator(products, page)
                return {
                    'products': paginator['products'],
                    'product-category': product_category,
                    'paginator-data': paginator['paginator_data']
                }
            else:
                return error_list
        else:
            return error_list

    def fast_filter(self, query_set, criteria, mode='text'):
        products = []

        if mode == 'text':
            for product in query_set:
                if criteria in product.description:
                    products.append(product)

        elif mode == 'number':
            for product in query_set:
                try:
                    inp_data = criteria[1]
                    try:
                        min = int(inp_data[criteria[2]+'-min'])
                    except:
                        min = 0
                    try:
                        max = int(inp_data[criteria[2]+'-max'])
                    except:
                        max = 0

                    product_amount = product.amount
                    if max == 0:
                        if product_amount > min:
                            products.append(product)
                    else:
                        if product_amount > min and product_amount < max:
                            products.append(product)
                except:
                    pass
        return products

    def valid_paginator(self, query_set, page_number=1, count_objects=50):
        count_pages = round(len(query_set) / count_objects)
        if page_number > count_pages and page_number <= 0:
            page_number = 1
            objects = query_set[0: count_objects]
            print(len(objects), 0, count_objects)
        else:
            start = (page_number-1)*count_objects
            objects = query_set[start: start+count_objects]
            print(len(objects), start, start+count_objects)
        return {
            'products': objects,
            'paginator_data': {
                'count-pages': count_pages,
                'page-number': page_number,
            }
        }

class UpdateProductMixin(AddProductMixin):
    def get(self, request, id):
        if request.is_ajax():
            try:
                user = CustomUser.objects.get(id=auth.get_user(request).id)
                product = Product.objects.get(author=user, id=id)

                data = ast.literal_eval(product.description)

                return JsonResponse({'result': data})
            except:
                return JsonResponse({'reuslt': 'error'})
        else:
            try:
                user = CustomUser.objects.get(id=auth.get_user(request).id)
                product = Product.objects.get(author=user, id=id)

                return render(request, 'edit_product.html', context={
                    'product': product
                })
            except:
                return redirect('/market/products/')

    def post(self, request, id):
        if request.is_ajax():
            data = request.POST.get('data')
            data = json.loads(decrypt(data, request.COOKIES['csrftoken'][0:16]))
            user_id = auth.get_user(request).id
            args = {}
            try:
                cards = UserCard.objects.filter(user=CustomUser.objects.get(id=user_id))
                if len(cards) == 0:
                    args['card_error'] = 'Щоб користуватися послугами HopePay потрібно додати банківську карту в вашому профілі'
            except:
                args['login_error'] = 'Увійдіть або Зареєструйтесь'

            if len(args) == 0:
                error_list = self.validate_data(data['category-data'])
                if len(error_list) > 0:
                    return JsonResponse({'error': 'error'})
                else:
                    res = self.validate_remittance({}, data)

                    if len(res['error_list']) == 0:
                        user = CustomUser.objects.get(id=auth.get_user(request).id)
                        product = Product.objects.filter(author=user, id=id)

                        product.update(
                            payment_desciption=data['description'],
                            amount=res['amount'],
                            currency=res['currency'],
                            postal_transfer=res['postal_transfer'],
                            seller=res['seller'],
                            payment_by_installments=res['pay'],
                            installments_count=res['parts'],
                            description=data['category-data'],
                            title=data['title'],
                            location=data['location'])
                        return JsonResponse({'result': 'OK'})
                    else:
                        return JsonResponse({'error': 'error'})
            else:
                return JsonResponse({'error': 'error'})

class DeleteProductMixin(View):
    def post(self, request, id):
        if request.is_ajax():
            try:
                user = CustomUser.objects.get(id=auth.get_user(request).id)
                product = Product.objects.filter(author=user, id=id)
                changes = product[0].product_changes.all().delete()
                product.delete()
                return JsonResponse({'result': 'success'})
            except:
                return JsonResponse({'result': 'error'})

class ProductsMixin(AddProductMixin):
    def get(self, request):
        if request.is_ajax():
            input_data = json.loads(request.GET.get('data'))
            try:
                page_number = int(request.GET.get('page'))
            except:
                page_number = 1
            view_mode = request.GET.get('mode')
            result = self.validate_data(input_data, page_number, mode='filter', view_mode=view_mode)
            try:
                products = result['products']
            except:
                products = []
            data = []
            try:
                main_image = [img for img in i.images.all()][0]
            except:
                main_image = []

            for i in products:
                data.append({
                    'title': i.title,
                    'location': i.location,
                    'category': result['product-category'],
                    'price': i.amount,
                    'id': i.id,
                    'images': main_image
                })
            return JsonResponse({
                    'products': json.dumps(data),
                    'paginator-data': result['paginator-data']
                })
        else:
            return render(request, 'products.html')

class ActivateOrDeactiveMixin(View):
    def post(self, request, id):
        if request.is_ajax():
            data = request.POST.get('mode')
            if data == 'activate' or data == 'deactivate':
                try:
                    user = CustomUser.objects.get(id=auth.get_user(request).id)
                    product = Product.objects.filter(id=id, author=user)
                    if data == 'activate':
                        product.update(active_status=True)
                    else:
                        product.update(active_status=False)
                    return JsonResponse({'result': 'success'})
                except:
                    return JsonResponse({'result': 'error'})
            else:
                return JsonResponse({'result': 'error'})

class ConfirmRateMixin(View):
    def post(self, request, id):
        if request.is_ajax():
            rate_id = request.POST.get('id')

            user_id = auth.get_user(request).id
            try:
                user = CustomUser.objects.get(id=user_id)
                product = Product.objects.get(id=id, author=user)
            except:
                return JsonResponse({'error': 'error'})
            rate = ChangesAwaitingConfirmation.objects.filter(product=product, id=rate_id)
            unique_link = gen_link()
            if product.seller == True:
                Remittance.objects.create(remittance_seller=user, remittance_customer=rate[0].author,
                                          unique_link=unique_link, postal_transfer=True,
                                          amount=rate[0].amount, currency='UAH',
                                          payment_desciption=rate[0].description, payment_by_installments=rate[0].payment_by_installments,
                                          installments_count=rate[0].installments_count)
            elif product.seller == False:
                Remittance.objects.create(remittance_seller=rate[0].author, remittance_customer=user,
                                          unique_link=unique_link, postal_transfer=True,
                                          amount=rate[0].amount, currency='UAH',
                                          payment_desciption=rate[0].description, payment_by_installments=rate[0].payment_by_installments,
                                          installments_count=rate[0].installments_count)
            rate.delete()
            #send email
            return JsonResponse({'result': 'success'})

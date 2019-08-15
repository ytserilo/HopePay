import asyncio, aiohttp, json, time, sys, os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HopePay.settings')

sys.path.append('/home/yardzen/HopePay/HopePay')
django.setup()

from Remittance.models import Remittance
from liqpay.liqpay import LiqPay
from celery import app

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

public_key = "sandbox_i22708126141"
private_key = b"sandbox_DRE62ozXPO4UyfUU8jUGlUls2F7LV8SGussS1jxE"

async def get_new_postal_data(session, remittance):
    apikey = '5c91a4239f54889de26a9a4a29698f16'

    request_url = "https://api.novaposhta.ua/v2.0/json/"
    json_req = {
            "apiKey": "{}".format(apikey),
            "modelName": "TrackingDocument",
            "calledMethod": "getStatusDocuments",
            "methodProperties": {
                "Documents":[
                    {
                        "DocumentNumber": "{}".format(remittance.postal_code),
                    }]
            }
        }
    async with session.get(request_url, data=json.dumps(json_req)) as response:

        data = await response.read()
        data = json.loads(data)


        if time.time() - float(remittance.date_payed) > 1874880:
            if data['data'][0]['StatusCode'] == '9' or data['data'][0]['StatusCode'] == '3':
                liqpay = LiqPay(public_key, private_key)
                res = liqpay.api("request", {
                    "action"        : "hold_completion",
                    "version"       : "3",
                    "order_id"      : remittance.liqpay_order_id,
                    "amount"        : str(float(remittance.amount * 0.01)),
                })

                res = liqpay.api("request", {
                    "action"         : "p2p",
                    "version"        : "3",
                    "phone"          : remittance.remittance_customer.usercard.phone_number,
                    "amount"         : remittance.amount,
                    "currency"       : "UAH",
                    "description"    : remittance.payment_desciption,
                    "order_id"       : str(gen_link()),
                    "receiver_card"  : remittance.remittance_seller.usercard.card_number,
                    "card"           : remittance.remittance_customer.usercard.card_number,
                    "card_exp_month" : remittance.remittance_customer.usercard.month_card,
                    "card_exp_year"  : remittance.remittance_customer.usercard.year_card,
                    "card_cvv"       : remittance.remittance_customer.usercard.cvv_card
                })

async def main():
    tasks = []
    remittances = Remittance.objects.exclude(successful=True).exclude(successful=False).exclude(shipped=False).exclude(paid=False)
    l_rem = len(remittances)

    async with aiohttp.ClientSession() as session:
        for rem in remittances:
            task = asyncio.create_task(get_new_postal_data(session, rem))
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    while True:

        asyncio.run(main())
        time.sleep(3600)

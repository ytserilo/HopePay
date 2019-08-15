from rest_framework.views import APIView
import json

class CreateRemitanceApi(APIView, RemittanceApi):

    def post(self, request):
        result = self.create_remitance(request)
        return Response(json.dump(result))

class ChangeRemittanceApi(APIView, RemittanceApi):

    def put(self, request, id):
        result = self.change_remittance(request)
        if result['update']:
            remittance = result['update']

            fin_array = {
                'description': remittance.description,
                'amount': remittance.amount,
                'currency': remittance.currency,
            }
            return Response(json.dump(fin_array))
        else:
            return Response(json.dump(result))

class CreateInviteCodeApi(APIView, RemittanceApi):

    def post(self, request, id):
        result = self.create_invite_link(request)
        return Response(json.dump(result))


class ConfirmInviteCodeApi(APIView, RemittanceApi):

    def get(self, request, code):
        result = confirm_invite_code(request, code)
        return Response(json.dump(result))

class PayApi(APIView, RemittanceApi):
    def pay_func(self, data, remittance):
        liqpay = LiqPay(public_key, private_key)

        res = liqpay.api("request", {
            "action"         : "p2p",
            "version"        : "3",
            "phone"          : data["phone"],
            "amount"         : remittance.amount,
            "currency"       : remittance.currency,
            "description"    : remittance.description,
            "order_id"       : remittance.id,
            "receiver_card"  : '11111111111111',
            "card"           : data["card"],
            "card_exp_month" : data["card_exp_month"],
            "card_exp_year"  : data["card_exp_year"],
            "card_cvv"       : data["card_cvv"]
        })

    def post(self, request, id):
        data, remittance = self.pay(request, id)

        self.pay_func(data, remittance)
        return Response(json.dump({'pay_status': remittance.paid}))

class SendProductApi(APIView, RemittanceApi):
    def put(self, request, id):
        result = self.send_product(request, id))
        return Response(json.dump(result)

class CencellRemittanceApi(APIView, RemittanceApi):
    def put(self, request, id):
        result = self.cencell_remittance(request, id)
        return Response(json.dump(result))

class ConfirmRemittanceApi(APIView, RemittanceApi):
    def post(self, request, id):
        result = self.confirm_remittance(request, id)
        return Response(json.dump(result))

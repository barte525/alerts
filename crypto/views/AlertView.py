from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from crypto.models.Alert import Alert
import json
import requests
from crypto.services.alert_checker import check_alert
from crypto.const import CURRENCIES, METALS, CRYPTOS

server_url = "http://host.docker.internal:5000/api/"


class AlertView(APIView):
    currencies = CURRENCIES
    metals = METALS
    cryptos = CRYPTOS

    def post(self, request):
        json_data = json.loads(request.body)
        print(json_data)
        email = json_data.get('email', '')
        currency = json_data.get('targetCurrency', '')
        value = json_data.get('targetValue', '')
        origin_asset_name = json_data.get('originAssetName', '')
        current_value = json_data.get('currentValue', '')
        on_email = json_data.get('onEmail', True)
        currencies = self.get_currencies_from_server()
        print(email, currency, value, origin_asset_name, current_value)
        if not all([email, currency, origin_asset_name]) or value == '' or current_value == '':
            return HttpResponse("Request does not contain all required query", status=400)
        if currency not in currencies and origin_asset_name not in currencies:
            return HttpResponse("This currency is not available", status=400)
        alert_when_increases = value >= current_value
        created__alert = Alert(alert_value=value, email=email, origin_asset_name=origin_asset_name,
                               currency=currency, alert_when_increases=alert_when_increases, active=True,
                               on_email=on_email)
        created__alert.save()

        return JsonResponse(self.parse_alert(created__alert), status=200)

    #do rozdzielenia na currency i wszystkie aktywa, zastanowic sie na ogarnieciem klas, na razie dziala na wszystkich
    @staticmethod
    def get_currencies_from_server():
        response = requests.get(f'{server_url}assets', verify=False).json()
        response_currencies = [asset['name'] for asset in response if asset['category'] == 'currency']
        return response_currencies

    def get(self, request):
        email = request.GET.get('email', '')
        if not email:
            alerts = Alert.objects.all()
        else:
            alerts = Alert.objects.filter(email=email)
        alerts_resp = []
        for alert in alerts:
            alert_resp = self.parse_alert(alert)
            alerts_resp.append(alert_resp)
        return JsonResponse(alerts_resp, safe=False)

    # def patch(self, request):
    #     json_data = json.loads(request.body)
    #     email = json_data.get('email', '')
    #     currency = json_data.get('currency', '')
    #     value = json_data.get('value', '')
    #     origin_asset_name = json_data.get('origin_asset_name', '')
    #     current_value = json_data.get('current_value', '')
    #     currencies = self.get_currencies_from_server()
    #     try:
    #         alert = Alert.objects.get(id=id)
    #     except Alert.DoesNotExist:
    #         return HttpResponse('Alert with given id does not exist', status=400)
    #     if origin_asset_name not in currencies or currency not in currencies:
    #         return HttpResponse("This currency is not available", status=400)
    #     if email:
    #         alert.email = email
    #     if currency:
    #         alert.currency = currency
    #     if origin_asset_name:
    #         alert.origin_asset_name = origin_asset_name
    #     if value and current_value:
    #         if not value or not current_value:
    #             return HttpResponse('Value requires current_value', status=400)
    #         alert_when_increases = value >= current_value
    #         alert.alert_when_increases = alert_when_increases
    #         alert.alert_value = value
    #     alert.save()
    #     return HttpResponse("Alert updated", status=200)

    def delete(self, request):
        id = request.GET.get('id', '')
        email = request.GET.get('email', '')
        if not id:
            return HttpResponse("Request does not contain all required query", status=400)
        try:
            alert = Alert.objects.get(id=id)
        except Alert.DoesNotExist:
            return HttpResponse('Alert with given id does not exist', status=400)
        if alert.email != email:
            return HttpResponse('Alert does not belong to this user', status=401)
        alert.delete()
        return HttpResponse("Alert deleted", status=200)

    def parse_alert(self, alert):
        if alert.origin_asset_name in self.cryptos:
            name = "crypto"
        elif alert.origin_asset_name in self.metals:
            name = "metal"
        else:
            name = "currency"
        return {
                "AlertId": alert.id,
                "OriginAssetName": alert.origin_asset_name,
                "Value": alert.alert_value,
                "Currency": alert.currency,
                "alert_when_increases": alert.alert_when_increases,
                "Active": alert.active,
                "OriginAssetType": name,
                "onEmail": alert.on_email
            }


def outher_check_alert(request):
    asset = request.GET.get('asset', '')
    response = list(requests.get(f'{server_url}asset-values', verify=False).json())
    check_alert(asset, response)
    return HttpResponse("Alerts checked", status=200)


def change_on_email_for_user(request):
    email = request.GET.get('email', '')
    on_email = request.GET.get('onEmail', '')
    if not email or (on_email != 'True' and on_email != 'False'):
        return HttpResponse("Request does not contain all required query", status=400)
    on_email_bool = True if on_email == 'True' else False
    Alert.objects.filter(email=email).update(on_email=on_email_bool)
    return HttpResponse("Alerts updated", status=200)

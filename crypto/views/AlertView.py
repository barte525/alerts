from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from crypto.models.Alert import Alert
from crypto.models.Asset import Asset
import json
from django.db.utils import IntegrityError


class AlertView(APIView):
    def post(self, request):
        json_data = json.loads(request.body)
        email = json_data.get('email', '')
        currency = json_data.get('currency', '')
        value = json_data.get('value', '')
        asset_name = json_data.get('asset_name')
        if not currency or not asset_name:
            return HttpResponse("Request does not contain all required query", status=400)
        if value == '': value = 0
        asset = Asset.objects.filter(name=asset_name)
        if len(asset) == 0:
            return HttpResponse("Asset with this name does not exist", status=400)
        idA = asset[0]
        alert_when_increases = value >= getattr(idA, "converter" + currency)
        try:
            created__alert = Alert(alert_value=value, email=email, idA=idA, currency=currency,
                                   alert_when_increases=alert_when_increases)
            created__alert.save()
        except IntegrityError:
            return HttpResponse("Currency must be: EUR/PLN/USD", status=400)
        return JsonResponse(parse_alert(created__alert), status=200)

    def get(self, request):
        email = request.GET.get('email', '')
        if not email:
            alerts = Alert.objects.all()
        else:
            alerts = Alert.objects.filter(email=email)
        alerts_resp = []
        for alert in alerts:
            alert_resp = parse_alert(alert)
            alerts_resp.append(alert_resp)
        return JsonResponse(alerts_resp, safe=False)

    def patch(self, request):
        json_data = json.loads(request.body)
        id = json_data.get('id', '')
        email = json_data.get('email', '')
        currency = json_data.get('currency', '')
        value = json_data.get('value', '')
        asset_name = json_data.get('asset_name', '')
        print('a_name', asset_name)
        try:
            alert = Alert.objects.get(id=id)
        except Alert.DoesNotExist:
            return HttpResponse('Alert with given id does not exist', status=400)
        if email:
            alert.email = email
        if currency:
            alert.currency = currency
        if asset_name:
            asset = Asset.objects.filter(name=asset_name)
            if len(asset) == 0:
                return HttpResponse("Asset with this name does not exist", status=400)
            alert.idA = asset[0]
        if value:
            idA = alert.idA
            alert_when_increases = float(value) >= getattr(idA, "converter" + alert.currency)
            alert.alert_when_increases = alert_when_increases
            alert.alert_value = float(value)
        try:
            alert.save()
        except IntegrityError:
            return HttpResponse("Currency must be: EUR/PLN/USD", status=400)
        return HttpResponse("Alert updated", status=200)

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


def parse_alert(alert):
    return {
            "id": alert.id,
            "asset_type": Asset.objects.get(id=alert.idA.id).asset_type,
            "value": alert.alert_value,
            "currency": alert.currency,
            "asset_name": Asset.objects.get(id=alert.idA.id).name,
            }


def get_all_al(request):
    email = request.GET.get('email', '')
    if not email:
        alerts = Alert.objects.all()
    else:
        alerts = Alert.objects.filter(email=email)
        if len(alerts) == 0:
            return HttpResponse("Alert with given email haven't been created", status=400)
    alerts_resp = []
    for alert in alerts:
        alert_resp = parse_alert(alert)
        alerts_resp.append(alert_resp)
    return JsonResponse(alerts_resp, safe=False)


def send_email_with_password(request):
    password = request.GET.get('password', '')
    email = request.GET.get('email', '')
    if not password or not email:
        return HttpResponse("Query is missing", status=400)
    Alert().send_email(email, '', '', '', password)
    return HttpResponse("Mail sent", status=200)
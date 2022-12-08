from time import sleep

from django.http import HttpResponse
from rest_framework.views import APIView
import json
from crypto.services.send_email import EmailSender

class ReportView(APIView):
    def post(self, request):
        json_data = json.loads(request.body)
        raports = []
        for raport in json_data:
            raports.append(raport)
        for raport in raports:
            if not (raport.get('email', False) and raport.get('currenctWalletValue', False) and
                    raport.get('currencyPreference', False)):
                return HttpResponse("Request does not contain all required query", status=400)
        emails = {}
        for raport in raports:
            email = raport.get('email')
            currenctWalletValue = raport.get('currenctWalletValue')
            walletValueWeekAgo = raport.get('walletValueWeekAgo', 0)
            if walletValueWeekAgo is None:
                walletValueWeekAgo = 0
            biggestAssetName = raport.get('biggestAssetName', None)
            biggestAssetValue = raport.get('biggestAssetValue', None)
            currencyPreference = raport.get('currencyPreference')
            if currencyPreference not in ['eur', 'usd', 'pln']:
                return HttpResponse("Currency preference is not valid", status=400)
            emails[email] = (currenctWalletValue, walletValueWeekAgo, biggestAssetName, biggestAssetValue, currencyPreference)
        email_sender = EmailSender()
        email_sender.send_raports(emails)
        return HttpResponse("Reports sent", status=200)
from django.db import models
from crypto.models import Asset
from crypto.models.consts import main_currencies
import smtplib
import ssl
from crypto.settings import env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.db.models import Q
import string, random


class Alert(models.Model):
    alert_value = models.FloatField(null=False)
    email = models.EmailField(null=False, max_length=254)
    currency = models.CharField(max_length=30)
    idA = models.ForeignKey(Asset, on_delete=models.CASCADE) #change to origin_asset_name
    alert_when_increases = models.BooleanField(default=True)

    dev_email = "financialallert@gmail.com"
    port = 465
    server_address = "smtp.gmail.com"
    message = MIMEMultipart("alternative")
    subject = "HowMoney Alert"
    password_subject = "HowMoney new password"
    message_text = """\
    {asset_name} hit your alert price: {price} {currency}! 
    """
    password_message_text = """\
    Your new password is: {password}. 
    """
    password_length = 10

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="crypto_alert_currency",
                check=models.Q(currency__in=main_currencies)
            )
        ]

    def send_email(self, receiver_mail, name, price, currency, new_password):
        if not new_password:
            self.format_message(currency, name, price, receiver_mail)
        else:
            self.format_password_message(receiver_mail, new_password)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.server_address, port=self.port, context=context) as server:
            server.login(self.dev_email, env('email_password'))
            server.sendmail(self.dev_email, receiver_mail, self.message.as_string())

    def format_message(self, currency, name, price, receiver_mail):
        self.message["Subject"] = self.subject + receiver_mail
        self.message["From"] = self.server_address
        self.message["To"] = receiver_mail
        message_text_attachment = MIMEText(self.message_text.format(asset_name=name, price=price, currency=currency),
                                           "plain")
        self.message.attach(message_text_attachment)

    def format_password_message(self, receiver_mail, new_password):
        self.message["Subject"] = self.password_subject
        self.message["From"] = self.server_address
        self.message["To"] = receiver_mail
        message_text_attachment = MIMEText(self.password_message_text.format(password=new_password), "plain")
        self.message.attach(message_text_attachment)

    # def check_alert(self, asset, currency):
    #     alerts_list = Alert.objects.filter(Q(idA=asset) & Q(currency=currency))
    #     new_price = float(Alert.get_converter_by_currency_code(asset, currency))
    #     for alert in alerts_list:
    #         alert_value = alert.alert_value
    #         if (new_price > alert_value) == alert.alert_when_increases or new_price == alert_value:
    #             self.send_email(alert.email, asset.name, alert_value, currency, "")
    #             alert.delete()

    @staticmethod
    def get_converter_by_currency_code(asset, currency_code):
        if currency_code == 'EUR':
            return asset.converterEUR
        if currency_code == 'PLN':
            return asset.converterPLN
        if currency_code == 'USD':
            return asset.converterUSD








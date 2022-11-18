
import smtplib
import ssl

from crypto.settings import env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crypto.const import METALS


class EmailSender:
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

    message_text_report = """\
    Total value of your wallet is {current_wallet_value}$ and {change} {change_value}% from last weak. You have most of your money in {biggest_asset_name}, in which you have {asset_name_change}% of your wallet.
     """
    message_text_report_equal = """\
        Total value of your wallet did not change from last weak. You have most of your money in {biggest_asset_name}, in which you have {asset_name_change}% of your wallet.
         """

    def send_email(self, receiver_mail):
        print("DUPA")
        self.message["Subject"] = self.subject + receiver_mail
        self.message["From"] = self.server_address
        self.message["To"] = receiver_mail
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.server_address, port=self.port, context=context) as server:
            server.login(self.dev_email, env('email_password'))
            server.sendmail(self.dev_email, receiver_mail, self.message.as_string())

    def format_alert_message(self, currency, name, price):
        message_text_attachment = MIMEText(self.message_text.format(asset_name=name, price=price, currency=currency),
                                           "plain")
        self.message.attach(message_text_attachment)

    def format_raport_message(self, current_wallet_value, wallet_value_week_ago, biggest_asset_name, biggest_asset_value):
        change_value = int((current_wallet_value - wallet_value_week_ago) / wallet_value_week_ago * 100)
        asset_name_change = int(biggest_asset_value/current_wallet_value*100)
        if biggest_asset_name not in METALS:
            biggest_asset_name = biggest_asset_name.upper()
        if change_value == 0:
            message_text_attachment = MIMEText(self.message_text_report_equal.format(
                biggest_asset_name=biggest_asset_name, asset_name_change=asset_name_change), "plain")
        else:
            change = "increased" if change_value > 0 else "descreased"
            message_text_attachment = MIMEText(self.message_text_report.format(
                current_wallet_value=current_wallet_value, change=change, change_value=change_value,
                biggest_asset_name=biggest_asset_name, asset_name_change=asset_name_change), "plain")
        print("alo", message_text_attachment)
        self.message.attach(message_text_attachment)

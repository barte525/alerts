import smtplib
import datetime

from crypto.settings import env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crypto.const import METALS, MESSAGE_TEXT


class EmailSender:
    dev_email = "financialallert@gmail.com"
    port = 465
    server_address = "smtp.gmail.com"
    message = MIMEMultipart("alternative")
    subject = "HowMoney Alert"
    password_subject = "HowMoney new password"
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

    def send_alerts(self, emails):
        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.dev_email, env('email_password'))
            for alert in emails:
                email = alert['email']
                data = alert['alert_msg']
                msg = self.format_alert_message(data[0], data[1], data[2])
                mail = MIMEMultipart()
                mail['from'] = self.server_address
                mail['to'] = email
                mail['subject'] = self.subject + " " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M') + " to " + \
                                  email
                mail.attach(msg)
                smtp.send_message(mail)

    def format_alert_message(self, currency, name, price):
        message_text_attachment = MIMEText(MESSAGE_TEXT.format(asset_name=name, price=price, currency=currency),
                                           "plain")
        return message_text_attachment

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
            change_value = -1 * change_value if change_value < 0 else change_value
            message_text_attachment = MIMEText(self.message_text_report.format(
                current_wallet_value=current_wallet_value, change=change, change_value=change_value,
                biggest_asset_name=biggest_asset_name, asset_name_change=asset_name_change), "plain")
        return message_text_attachment

    def send_raports(self, emails):
        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.dev_email, env('email_password'))
            for email, data in emails.items():
                msg = self.format_raport_message(data[0], data[1], data[2], data[3])
                mail = MIMEMultipart()
                mail['from'] = self.server_address
                mail['to'] = email
                mail['subject'] = self.subject + " " + datetime.datetime.now().strftime('%Y-%m-%d %H-%M') + " to " + \
                                  email
                mail.attach(msg)
                smtp.send_message(mail)

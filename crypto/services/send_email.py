
import smtplib
import ssl

from crypto.settings import env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
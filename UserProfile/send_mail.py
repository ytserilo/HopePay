from django.core.mail import send_mail, BadHeaderError
from django.utils.decorators import method_decorator
import smtplib

class SendMail:
    def send_mail(self, subject, message, email):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("hopepay.my@gmail.com", "Zzzhbr1111")
        server.sendmail("hopepay.my@gmail.com", email, message.encode())
        server.quit()

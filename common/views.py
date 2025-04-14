from django.shortcuts import render


from django.core.mail import send_mail
from django.conf import settings


def send_registration_email(email, name, message):
    subject = "Welcome to Our Platform!"
    message = message
    print(email, name)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

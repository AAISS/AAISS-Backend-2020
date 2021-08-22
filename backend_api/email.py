from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection


def send_simple_email(subject, email, body):
    message = body
    if 'gmail' not in email:
        connection = get_connection(
            backend=settings.ALT_EMAIL_BACKEND,
            fail_silently=False,
            username=settings.ALT_EMAIL_HOST_USER,
            use_tls=True,
            password=settings.ALT_EMAIL_HOST_PASSWORD,
            port=settings.ALT_EMAIL_PORT,
            host=settings.ALT_EMAIL_HOST
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email, ],
            connection=connection
        )
    else:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email, ]
        )
    msg.attach_alternative(message, 'text/html')
    msg.send()
    return {
        'message': 'successfully sent to : {}'.format(email)
    }

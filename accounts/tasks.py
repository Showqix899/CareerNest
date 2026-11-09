from celery import shared_task
from django.conf import settings 
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries":3},
)
    
def send_activation_email(email, full_name, activation_link):
    context = {"full_name": full_name, "activation_link": activation_link}

    text_body = render_to_string("accounts/emails/activation_email.txt", context)
    html_body = render_to_string("accounts/emails/activation_email.html", context)

    message = EmailMultiAlternatives(
        subject="Activate your account",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
# notifications/email_service.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_html_email(subject, recipients, template, context):
    """Envoie un email HTML (avec repli texte) à partir d'un gabarit."""
    html = render_to_string(template, context)
    text = strip_tags(html)
    message = EmailMultiAlternatives(subject, text, to=recipients)
    message.attach_alternative(html, 'text/html')
    message.send(fail_silently=True)

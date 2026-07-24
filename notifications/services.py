# notifications/services.py
from .models import Notification


def notify(recipient, message, url=''):
    """Crée une notification pour une personne."""
    if recipient is None:
        return
    Notification.objects.create(
        recipient=recipient, message=message, url=url)

def notify_many(recipients, message, url='', exclude=None):
    """Notifie plusieurs personnes, sans doublon, en excluant l'auteur."""
    vus = set()
    for user in recipients:
        if user is None or user == exclude or user.id in vus:
            continue
        vus.add(user.id)
        Notification.objects.create(
            recipient=user, message=message, url=url)

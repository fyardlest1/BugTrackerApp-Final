# tickets/tests_notifications.py
from django.test import TestCase
from django.urls import reverse
from accounts.models import Company, Roles
from projects.models import Project
from tickets.models import Ticket
from notifications.models import Notification
from tickets.tests_helpers import make_user


class CommentNotificationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name='Alpha')
        cls.auteur = make_user('auteur', cls.company, Roles.ADMIN)
        cls.rapporteur = make_user('rapporteur', cls.company, Roles.SUBMITTER)
        cls.projet = Project.objects.create(
            name='Site', company=cls.company)
        cls.ticket = Ticket.objects.create(
            title='Bug', project=cls.projet, submitter=cls.rapporteur)

    def test_le_commentaire_notifie_les_bonnes_personnes(self):
        self.client.force_login(self.auteur)
        self.client.post(
            reverse('tickets:add_comment', args=[self.ticket.pk]),
            {'content': 'Je regarde ça tout de suite.'})
        # Le rapporteur est prévenu
        self.assertTrue(Notification.objects.filter(
            recipient=self.rapporteur).exists())
        # L'auteur ne se notifie pas lui-même
        self.assertFalse(Notification.objects.filter(
            recipient=self.auteur).exists())

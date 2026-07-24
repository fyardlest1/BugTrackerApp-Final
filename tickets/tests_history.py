# tickets/tests_history.py
from django.test import TestCase
from accounts.models import Company, Roles
from projects.models import Project
from tickets.models import Ticket, TicketHistory, TicketStatus
from tickets.tests_helpers import make_user


class TicketHistoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name='Alpha')
        cls.user = make_user('alice', cls.company, Roles.ADMIN)
        cls.projet = Project.objects.create(
            name='Site', company=cls.company)
        cls.ticket = Ticket.objects.create(
            title='Bug', project=cls.projet, submitter=cls.user)

    def test_changement_de_statut_est_journalise(self):
        self.ticket.status = TicketStatus.RESOLVED
        self.ticket._history_author = self.user
        self.ticket.save()
        ligne = TicketHistory.objects.get(
            ticket=self.ticket, field='status')
        self.assertEqual(ligne.new_value, 'Résolu')
        self.assertEqual(ligne.author, self.user)

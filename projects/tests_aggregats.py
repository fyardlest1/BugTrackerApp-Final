# projects/tests_aggregats.py
from django.test import TestCase
from django.db.models import Count, Q
from accounts.models import Company, Roles
from projects.models import Project
from tickets.models import Ticket, TicketStatus
from tickets.tests_helpers import make_user


class TicketsActifsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name='Alpha')
        cls.user = make_user('alice', cls.company, Roles.ADMIN)
        cls.projet = Project.objects.create(
            name='Site', company=cls.company)
        Ticket.objects.create(title='Ouvert', project=cls.projet,
            submitter=cls.user, status=TicketStatus.NEW)
        Ticket.objects.create(title='Fini', project=cls.projet,
            submitter=cls.user, status=TicketStatus.RESOLVED)

    def test_compte_uniquement_les_tickets_actifs(self):
        projet = Project.objects.annotate(
            tickets_actifs=Count('tickets', filter=(
                Q(tickets__archived=False)
                & ~Q(tickets__status=TicketStatus.RESOLVED)))
        ).get(pk=self.projet.pk)
        self.assertEqual(projet.tickets_actifs, 1)

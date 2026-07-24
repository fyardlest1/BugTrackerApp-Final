# api/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import Company, Roles
from projects.models import Project
from tickets.models import Ticket
from tickets.tests_helpers import make_user


class TicketAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alpha = Company.objects.create(name='Alpha')
        cls.beta = Company.objects.create(name='Beta')
        cls.alice = make_user('alice', cls.alpha, Roles.ADMIN)
        cls.bob = make_user('bob', cls.beta, Roles.ADMIN)
        cls.projet_beta = Project.objects.create(
            name='Site Beta', company=cls.beta)
        cls.ticket_beta = Ticket.objects.create(
            title='Secret Beta', project=cls.projet_beta,
            submitter=cls.bob)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.alice)

    def test_ticket_autre_entreprise_invisible(self):
        response = self.client.get(
            f'/api/tickets/{self.ticket_beta.pk}/')
        self.assertEqual(response.status_code, 404)

    def test_creation_force_le_rapporteur(self):
        projet = Project.objects.create(
            name='Site Alpha', company=self.alpha)
        response = self.client.post('/api/tickets/', {
            'title': 'Nouveau bug', 'description': 'Détails',
            'priority': 'Low', 'project': projet.pk})
        self.assertEqual(response.status_code, 201)
        cree = Ticket.objects.get(title='Nouveau bug')
        self.assertEqual(cree.submitter, self.alice)


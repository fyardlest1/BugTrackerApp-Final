# tickets/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from accounts.models import Company, Roles
from projects.models import Project
from tickets.models import Ticket


User = get_user_model()

class CompanyIsolationTest(TestCase):
    def setUp(self):
        self.alpha = Company.objects.create(name='Alpha')
        self.beta = Company.objects.create(name='Beta')
        self.alice = User.objects.create_user(
            'alice', password='pass', company=self.alpha)
        self.bob = User.objects.create_user(
            'bob', password='pass', company=self.beta)
        projet_beta = Project.objects.create(
            company=self.beta, name='Projet Beta')
        self.ticket_beta = Ticket.objects.create(
            project=projet_beta, title='Bug Beta',
            description='x', submitter=self.bob)

    def test_utilisateur_ne_voit_pas_ticket_autre_entreprise(self):
        self.client.force_login(self.alice)
        url = reverse('tickets:detail', args=[self.ticket_beta.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class RolePermissionTest(TestCase):
    def setUp(self):
        for role in Roles.values:
            Group.objects.get_or_create(name=role)
        self.company = Company.objects.create(name='Alpha')
        self.dev = User.objects.create_user(
            'dev', password='pass', company=self.company)
        self.dev.groups.add(Group.objects.get(name=Roles.DEVELOPER))
        self.projet = Project.objects.create(
            company=self.company, name='Projet')

    def test_developpeur_ne_peut_pas_modifier_projet(self):
        self.client.force_login(self.dev)
        url = reverse('projects:update', args=[self.projet.pk])
        response = self.client.post(
            url, {'name': 'Piraté', 'description': ''})
        self.assertEqual(response.status_code, 403)

# tickets/tests_services.py
from django.test import TestCase
from django.core.exceptions import PermissionDenied
from accounts.models import Company, Roles
from projects.models import Project
from tickets.models import Ticket
from tickets.services import assign_developer
from tickets.tests_helpers import make_user


class AssignDeveloperTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name='Alpha')
        cls.admin = make_user('admin', cls.company, Roles.ADMIN)
        cls.dev = make_user('dev', cls.company, Roles.DEVELOPER)
        cls.project = Project.objects.create(
            name='Site', company=cls.company)
        cls.project.members.add(cls.dev)          # <-- le développeur devient membre
        cls.ticket = Ticket.objects.create(
            title='Bug', project=cls.project, submitter=cls.admin)

    def test_admin_peut_assigner(self):
        assign_developer(self.admin, self.ticket, self.dev)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.developer, self.dev)

    def test_developpeur_ne_peut_pas_assigner(self):
        with self.assertRaises(PermissionDenied):
            assign_developer(self.dev, self.ticket, self.dev)

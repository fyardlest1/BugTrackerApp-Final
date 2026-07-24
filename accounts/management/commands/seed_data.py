# accounts/management/commands/seed_data.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from faker import Faker
from accounts.models import CustomUser, Company, Roles
from projects.models import Project
from tickets.models import Ticket, TicketStatus, TicketPriority


class Command(BaseCommand):
    help = 'Génère des données de démonstration'
    
    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
            help='Supprime les données existantes avant de regénérer')

    def handle(self, *args, **options):
        fake = Faker('fr_FR')
        
        if options['flush']:
            Company.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete()
            
        for role in Roles.values:
            Group.objects.get_or_create(name=role)

        for _ in range(5):              # 3 entreprises
            company = Company.objects.create(
                name=fake.company(), 
                description=fake.catch_phrase()
            )
            
            for role in [Roles.ADMIN, Roles.PROJECT_MANAGER,
                        Roles.DEVELOPER, Roles.SUBMITTER]:
                user = CustomUser.objects.create_user(
                    username=fake.unique.user_name(),
                    email=fake.email(),
                    password='Demo1234!',
                    company=company
                )
                user.groups.add(Group.objects.get(name=role))

            membres = list(company.members.all())
            
            for _ in range(random.randint(2, 4)):    # projets
                projet = Project.objects.create(
                    company=company,
                    name=fake.catch_phrase(),
                    description=fake.text(),
                    manager=random.choice(membres)
                )
                projet.members.set(membres)

                for _ in range(random.randint(3, 8)):  # tickets
                    Ticket.objects.create(
                        project=projet,
                        title=fake.sentence(),
                        description=fake.paragraph(),
                        status=random.choice(TicketStatus.values),
                        priority=random.choice(TicketPriority.values),
                        submitter=random.choice(membres)
                    )

        self.stdout.write(self.style.SUCCESS('Données générées avec succès.'))
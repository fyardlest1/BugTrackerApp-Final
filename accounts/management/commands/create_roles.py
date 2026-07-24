# accounts/management/commands/create_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import Roles


class Command(BaseCommand):
    help = "Cree les groupes de rôles de l'application"
    
    def handle(self, *args, **options):
        for role in Roles.values:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Rôle "{role}" créé avec succès.'))
            else:
                self.stdout.write(self.style.WARNING(f'Rôle "{role}" existe déjà.'))
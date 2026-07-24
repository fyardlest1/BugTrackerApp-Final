# accounts/management/commands/create_demo.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from accounts.models import Company, Roles


# 1. Cartographie des rôles et des noms d'utilisateurs associés pour la démo
# Ce dictionnaire associe chaque rôle de l'application à un identifiant (username) unique de démonstration
DEMO = {
    Roles.ADMIN: 'demo.admin',
    Roles.PROJECT_MANAGER: 'demo.pm',
    Roles.DEVELOPER: 'demo.dev',
    Roles.SUBMITTER: 'demo.submitter',
}

class Command(BaseCommand):
    help = 'Crée les comptes de démonstration'

    def handle(self, *args, **options):
        # 2. Récupération dynamique du modèle utilisateur personnalisé configuré dans Django
        User = get_user_model()
        
        # 3. Initialisation de l'entité Entreprise de démonstration
        # Récupère l'entreprise si elle existe déjà, ou la crée avec ce nom (le '_' ignore le booléen 'created' renvoyé par Django)
        company, _ = Company.objects.get_or_create(name='Entreprise Démo')
        
        # 4. Boucle de création et de mise à jour des comptes pour chaque rôle
        for role, username in DEMO.items():
            # Récupère ou crée l'utilisateur avec le 'username' spécifié, en lui assignant l'entreprise par défaut
            user, _ = User.objects.get_or_create(
                username=username, defaults={'company': company})
            
            # 5. Synchronisation des informations de sécurité et d'affiliation
            # On force la réassignation de l'entreprise et on applique un mot de passe standardisé
            user.company = company
            user.set_password('Demo1234!') # Gère automatiquement le hachage du mot de passe
            user.save()
            
            # 6. Assignation des permissions Django via les Groupes
            # Nettoie les anciens groupes de l'utilisateur et lui associe uniquement le groupe correspondant à son rôle
            user.groups.set([Group.objects.get(name=role)])
            
        # 7. Notification de succès dans la console
        # Affiche un message de réussite colorisé en vert (style SUCCESS) dans le terminal
        self.stdout.write(self.style.SUCCESS('Comptes de démo prêts.'))

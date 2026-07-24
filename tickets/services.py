# tickets/services.py
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from accounts.models import Roles
from notifications.services import notify


def assign_developer(actor, ticket, developer):    
    # 1. Vérification de la cohérence de l'entreprise (isolation des données)
    # On s'assure que l'acteur qui effectue l'action appartient à la même entreprise que le projet du ticket
    project = ticket.project
    if project.company_id != actor.company_id:
        raise PermissionDenied
    
    # 2. Définition des règles d'autorisation pour l'attribution
    # Seul un Administrateur ou le Chef de projet assigné à ce projet spécifique peut effectuer cette action
    can_assign = actor.role == Roles.ADMIN or (
        actor.role == Roles.PROJECT_MANAGER
        and project.manager_id == actor.id)
    
    # 3. Validation des permissions de l'acteur
    # Si l'acteur n'est ni Admin ni le Chef de projet attitré, l'accès est refusé
    if not can_assign:
        raise PermissionDenied
    
    # 4. Vérification des critères d'éligibilité du développeur cible
    # On vérifie d'une part que son rôle est bien "Développeur" et d'autre part qu'il fait partie des membres du projet
    is_dev = developer.role == Roles.DEVELOPER
    is_member = project.members.filter(pk=developer.pk).exists()
    
    # 5. Validation finale de l'éligibilité du développeur
    # Si le profil ciblé n'est pas un développeur ou s'il n'est pas membre du projet, on lève une exception explicite
    if not (is_dev and is_member):
        raise PermissionDenied("Le ticket ne peut être assigné qu'à un développeur membre du projet.")
    
    # 6. Assignation et sauvegarde
    # On attribue le développeur au ticket puis on enregistre la modification en base de données
    ticket.developer = developer
    ticket._history_author = actor      # <-- on attribue le changement
    ticket.save()
    
    # Quand un développeur reçoit un ticket, il doit le savoir
    notify(developer,
        f'Un ticket vous a été assigné : {ticket.title}',
        reverse('tickets:detail', args=[ticket.id]))


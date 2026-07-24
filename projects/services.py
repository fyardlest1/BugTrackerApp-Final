# projects/services.py
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from notifications.services import notify

from accounts.models import Roles
from notifications.models import Notification


def assign_project_manager(actor, project, pm):
    # 1. Vérification de la cohérence de l'entreprise (isolation des données)
    # On s'assure que l'acteur qui tente de faire la modification appartient à la même entreprise que le projet
    if project.company_id != actor.company_id:
        raise PermissionDenied
    
    # 2. Définition des droits de l'acteur
    # Un utilisateur peut faire cette action s'il est Administrateur, ou s'il est Chef de projet et qu'il s'assigne lui-même
    is_admin = actor.role == Roles.ADMIN
    is_self_pm = actor.role == Roles.PROJECT_MANAGER and pm.id == actor.id
    
    # 3. Validation des permissions de l'acteur
    # Si l'acteur n'est ni Admin, ni en train de s'assigner lui-même comme Chef de projet, l'accès est refusé
    if not (is_admin or is_self_pm):
        raise PermissionDenied
        
    # 4. Vérification des critères d'éligibilité du Chef de projet cible
    # On s'assure que la cible possède bien le rôle "Chef de projet" ET qu'elle appartient à la même entreprise que le projet
    if pm.role != Roles.PROJECT_MANAGER or pm.company_id != project.company_id:
        raise PermissionDenied
        
    # 5. Assignation et sauvegarde
    # On attribue le Chef de projet (pm) au projet, puis on enregistre les modifications en base de données
    project.manager = pm
    project.save()
    
    Notification.objects.create(
        recipient=pm,
        message=f"Vous avez été assigné au projet {project.name}.",
        url=reverse('projects:detail', args=[project.id]))

    notify(pm,
        f'Vous avez été assigné au projet {project.name}',
        reverse('projects:detail', args=[project.id]))


def add_member(actor, project, member):
    if project.company_id != actor.company_id:
        raise PermissionDenied
    can = actor.role == Roles.ADMIN or (
        actor.role == Roles.PROJECT_MANAGER
        and project.manager_id == actor.id)
    if not can:
        raise PermissionDenied
    if member.company_id != project.company_id:
        raise PermissionDenied
    project.members.add(member)

from accounts.models import Roles

def is_admin(user):
    # 1. Vérification du rôle Administrateur
    # Renvoie True si l'utilisateur possède le rôle d'administrateur, sinon False
    return user.role == Roles.ADMIN

def can_create_project(user):
    # 1. Permission de création de projet
    # Seuls les utilisateurs ayant le rôle d'Administrateur ou de Chef de projet sont autorisés à créer un projet
    return user.role in (Roles.ADMIN, Roles.PROJECT_MANAGER)

def can_manage_project(user, project):
    # 2. Cohérence de l'entreprise (Projet)
    # Interdit l'accès immédiat si l'utilisateur et le projet n'appartiennent pas à la même entreprise
    if user.company_id != project.company_id:
        return False
        
    # 3. Droits d'administration pour le projet
    # Un administrateur de l'entreprise a automatiquement le droit de gérer le projet
    if is_admin(user):
        return True
        
    # 4. Vérification du Chef de projet attitré
    # Autorise l'accès si l'utilisateur est un Chef de projet ET qu'il est explicitement assigné à ce projet
    return (user.role == Roles.PROJECT_MANAGER
            and project.manager_id == user.id)

def can_edit_ticket(user, ticket):
    # 5. Cohérence de l'entreprise (Ticket)
    # Récupère le projet lié et s'assure que l'utilisateur appartient à la même entreprise que ce projet
    project = ticket.project
    if user.company_id != project.company_id:
        return False
        
    # 6. Droits des super-utilisateurs du projet
    # Autorise la modification si l'utilisateur est Admin ou s'il est le Chef de projet responsable de ce projet
    if is_admin(user) or project.manager_id == user.id:
        return True
        
    # 7. Droits du Développeur assigné
    # Autorise la modification si l'utilisateur est un Développeur ET qu'il est personnellement assigné à ce ticket
    if user.role == Roles.DEVELOPER and ticket.developer_id == user.id:
        return True
        
    # 8. Droits de l'auteur du ticket (Créateur)
    # Par défaut, si aucune condition précédente n'est remplie, on autorise la modification uniquement si l'utilisateur est celui qui a créé (soumis) le ticket
    return ticket.submitter_id == user.id

def can_comment_ticket(user, ticket):
    # 2. Cohérence de l'entreprise (Ticket)
    # On récupère le projet lié et on refuse l'accès si l'utilisateur et le projet n'appartiennent pas à la même entreprise
    project = ticket.project
    if user.company_id != project.company_id:
        return False
        
    # 3. Droits des responsables
    # Un Administrateur ou le Chef de projet responsable du projet lié au ticket peut toujours ajouter un commentaire
    if is_admin(user) or project.manager_id == user.id:
        return True
        
    # 4. Droits des intervenants directs du ticket
    # Un utilisateur peut commenter si et seulement s'il est le créateur du ticket (submitter) ou le développeur assigné à celui-ci
    return user.id in (ticket.submitter_id, ticket.developer_id)

# BONUS
def can_manage_members(user, project):
    """Affecter ou retirer des membres (développeurs, rapporteurs) d'un projet.
    Administrateurs pour tout projet de l'entreprise ; chef de projet
    seulement pour les projets qu'il gère."""
    return can_manage_project(user, project)

def can_moderate(user, ticket):
    """Modifier ou supprimer n'importe quel commentaire ou pièce jointe d'un
    ticket, au-delà de son propre contenu : administrateurs et chef du projet."""
    project = ticket.project
    if user.company_id != project.company_id:
        return False
    return is_admin(user) or project.manager_id == user.id
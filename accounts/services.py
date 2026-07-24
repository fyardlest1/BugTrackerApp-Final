# accounts/services.py
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from .models import Roles


def change_user_role(actor, target, new_role):
    """actor change le rôle de target. Règles de sécurité incluses."""
    if actor.role != Roles.ADMIN:
        raise PermissionDenied("Seul un administrateur peut changer un rôle.")
    if target.company_id != actor.company_id:
        raise PermissionDenied("Cible d'une autre entreprise.")
    if target.id == actor.id:
        raise PermissionDenied("Un admin ne change pas son propre rôle.")

    target.groups.clear()
    target.groups.add(Group.objects.get(name=new_role))

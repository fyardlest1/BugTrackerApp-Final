# tickets/tests_helpers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def make_user(username, company, role=None):
    """Crée un utilisateur, éventuellement doté d'un rôle (un groupe)."""
    user = User.objects.create_user(
        username=username, password='motdepasse123', company=company)
    if role:
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
    return user

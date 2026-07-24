# accounts/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


# Creation d'un modèle de base pour tous les modèles de l'application
class BaseModel(models.Model):
    """
    Ce modèle de base fournira des champs communs tels que id, 
    created_at et updated_at à tous les modèles qui en héritent.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Indique que ce modèle est abstrait et ne sera pas créé dans la base de données
    class Meta:
        abstract = True


# Creation d'un modèle pour représenter une entreprise
class Company(BaseModel):
    """
    Ce modèle représente une entreprise. Il contient des informations de base
    telles que le nom, la description et le logo de l'entreprise.
    """
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    
    def members_in_role(self, role):
        return self.members.filter(groups__name=role)
    
    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"

    def __str__(self):
        return self.name


# Creation d'un modèle utilisateur personnalisé en héritant de AbstractUser
class CustomUser(AbstractUser):
    """
    Ce modèle représente un utilisateur de l'application. Il contient des informations de base
    telles que le nom, le prénom, l'email et le mot de passe.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    @property
    def role(self):
        group = self.groups.first()
        return group.name if group else None
    
    @property
    def role_label(self):
        if self.role is None:
            return None
        try:
            return Roles(self.role).label
        except ValueError:
            return self.role


class Roles(models.TextChoices):
    """
    Ce modèle représente les rôles d'un utilisateur dans l'application.
    Il contient cinq rôles : Admin, ProjectManager, Developer, Submitter et DemoUser.
    """
    ADMIN = 'Admin', 'Administrateur'
    PROJECT_MANAGER = 'ProjectManager', 'Chef de projet'
    DEVELOPER = 'Developer', 'Développeur'
    SUBMITTER = 'Submitter', 'Rapporteur'
    DEMO = 'DemoUser', 'Démo'
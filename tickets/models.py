# tickets/models.py
from django.db import models
from accounts.models import BaseModel
from pathlib import Path


class TicketStatus(models.TextChoices):
    NEW = 'New', 'Nouveau'
    IN_DEVELOPMENT = 'InDevelopment', 'En développement'
    TESTING = 'Testing', 'En test'
    RESOLVED = 'Resolved', 'Résolu'

class TicketPriority(models.TextChoices):
    LOW = 'Low', 'Basse'
    MEDIUM = 'Medium', 'Moyenne'
    HIGH = 'High', 'Haute'
    URGENT = 'Urgent', 'Urgente'


class Ticket(BaseModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.NEW)
    priority = models.CharField(max_length=10, choices=TicketPriority.choices, default=TicketPriority.MEDIUM)
    submitter = models.ForeignKey('accounts.CustomUser',
        on_delete=models.CASCADE, related_name='submitted_tickets')
    developer = models.ForeignKey('accounts.CustomUser',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tickets')
    archived = models.BooleanField(default=False)
    archived_by_project = models.BooleanField(default=False)
    
    CHAMPS_SUIVIS = ['status', 'priority', 'developer']
    
    def save(self, *args, **kwargs):
        """
            Surchargé la méthode save pour enregistrer l'historique des modifications.
            Compare les valeurs avant et après la sauvegarde pour chaque champ défini
            dans `CHAMPS_SUIVIS`. Si une modification est détectée, une entrée est 
            créée dans le modèle `TicketHistory`.

            Note:
                L'historique n'est généré que lors des modifications d'un ticket existant,
                pas lors de sa création initiale.

            Args:
                *args: Arguments positionnels transmis à la méthode `save` parent.
                **kwargs: Arguments nommés transmis à la méthode `save` parent.
                    Peut inclure `_history_author` s'il a été défini au préalable sur l'instance.
        """
        nouveau = self._state.adding          # création ou modification ?
        if not nouveau:
            ancien = Ticket.objects.get(pk=self.pk)
        super().save(*args, **kwargs)         # on enregistre d'abord
        if nouveau:
            return                            # rien à comparer à la création
        auteur = getattr(self, '_history_author', None)
        for champ in self.CHAMPS_SUIVIS:
            avant = getattr(ancien, champ)
            apres = getattr(self, champ)
            if avant != apres:
                TicketHistory.objects.create(
                    ticket=self, author=auteur, field=champ,
                    old_value=self._libelle(champ, avant),
                    new_value=self._libelle(champ, apres))
    
    def _libelle(self, champ, valeur):
        """Rend une valeur lisible pour le journal."""
        if valeur is None or valeur == '':
            return 'Non assigné' if champ == 'developer' else '(vide)'
        if champ == 'status':
            return dict(TicketStatus.choices).get(valeur, valeur)
        if champ == 'priority':
            return dict(TicketPriority.choices).get(valeur, valeur)
        return str(valeur)      # developer : affiche l'utilisateur


    def __str__(self):
        return self.title


class TicketComment(BaseModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    content = models.TextField()
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Commentaire de {self.author}'


class TicketAttachment(BaseModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    author = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    file_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    
    @property
    def kind(self):
        # Sécurité si content_type est vide ou None
        if not self.content_type:
            return 'fichier'
            
        content_type = self.content_type.lower().strip()

        # 1. Images
        if content_type.startswith('image/'):
            return 'image'
            
        # 2. PDF
        if content_type == 'application/pdf':
            return 'pdf'
            
        # 3. CSV / Tableurs (gère le CSV standard, Excel et le CSV Windows)
        if content_type in [
            "text/csv", 
            "application/csv", 
            "application/vnd.ms-excel", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]:
            return "spreadsheet"

        # 4. Word (gère le .doc et le .docx)
        # if content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        #     return "word"

        # 5. Archives (gère .zip, .rar, .7z, .tar, .gz)
        # if content_type in [
        #     "application/zip",
        #     "application/x-zip-compressed",
        #     "application/x-rar-compressed",
        #     "application/x-7z-compressed",
        #     "application/x-tar",
        #     "application/gzip",
        #     "application/x-gzip"
        # ]:
        #     return "archive"
            
        return 'fichier'


class TicketHistory(BaseModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    author = models.ForeignKey('accounts.CustomUser',
        on_delete=models.SET_NULL, null=True, blank=True)
    field = models.CharField(max_length=50)        # ex : 'status'
    old_value = models.CharField(max_length=150, blank=True)
    new_value = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['-created_at']               # le plus récent d'abord

    def __str__(self):
        return f'{self.field} : {self.old_value} -> {self.new_value}'




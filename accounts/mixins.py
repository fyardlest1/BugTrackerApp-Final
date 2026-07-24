# accounts/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin


class CompanyScopedMixin(LoginRequiredMixin):
    """
    Exige la connexion et ne renvoie que les objets de l'entreprise de l'utilisateur connecté.
    """
    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.company)

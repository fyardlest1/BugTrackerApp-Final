# accounts/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


class CompanyScopedMixin(LoginRequiredMixin):
    """
    Exige la connexion et ne renvoie que les objets de l'entreprise de l'utilisateur connecté.
    """
    def get_queryset(self):
        return super().get_queryset().filter(company=self.request.user.company)


class CompanyRequiredMixin(LoginRequiredMixin):
    """Exige que l'utilisateur connecté appartienne à une entreprise."""
    
    sans_entreprise_template = 'accounts/sans_entreprise.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.company_id is None:
            return render(request, self.sans_entreprise_template)
        return super().dispatch(request, *args, **kwargs)
# tickets/filters.py
import django_filters
from django import forms
from .models import Ticket, TicketStatus, TicketPriority


# 1. Définition des classes CSS réutilisables (classes utilitaires Tailwind CSS)
# Permet d'appliquer un style visuel uniforme (bordure, coins arrondis, padding, taille du texte) à tous les champs du formulaire
INLINE = 'border rounded px-3 py-2 text-sm'

class TicketFilter(django_filters.FilterSet):
    # 2. Filtre textuel pour le titre du ticket
    # Utilise 'icontains' pour une recherche insensible à la casse. 
    # Le widget personnalisé injecte les classes CSS et un texte d'aide (placeholder) dans le champ HTML final
    title = django_filters.CharFilter(
        lookup_expr='icontains', label='Titre',
        widget=forms.SearchInput(
            attrs={'class': INLINE, 'placeholder': 'Rechercher un ticket...'}))
            
    # 3. Filtre par liste déroulante pour le statut du ticket
    # Utilise un menu de sélection (Select) basé sur les choix prédéfinis du modèle Ticket (TicketStatus.choices)
    status = django_filters.ChoiceFilter(
        choices=TicketStatus.choices,
        widget=forms.Select(attrs={'class': INLINE}))
        
    # 4. Filtre par liste déroulante pour la priorité du ticket
    # Fonctionne comme le statut en limitant les options aux priorités existantes (TicketPriority.choices)
    priority = django_filters.ChoiceFilter(
        choices=TicketPriority.choices,
        widget=forms.Select(attrs={'class': INLINE}))

    class Meta:
        # 5. Configuration des métadonnées du FilterSet
        # On spécifie le modèle Django cible (Ticket) ainsi que la liste exhaustive des champs actifs pour le filtrage
        model = Ticket
        fields = ['title', 'status', 'priority']

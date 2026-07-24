# dashboard/views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from tickets.models import Ticket, TicketPriority, TicketStatus
from projects.models import Project


def home(request):
    if request.user.is_authenticated:
        # return redirect('projects:list')
        return redirect('dashboard')
    return render(request, 'landing.html')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        tickets = Ticket.objects.filter(
            project__company=user.company, archived=False)

        # Tickets par priorité
        context['priority_labels'] = [l for _, l in TicketPriority.choices]
        context['priority_data'] = [tickets.filter(priority=v).count() for v, _ in TicketPriority.choices]

        # Résolus contre non résolus
        resolved = tickets.filter(status=TicketStatus.RESOLVED).count()
        context['resolved'] = resolved
        context['unresolved'] = tickets.count() - resolved
        context['total'] = tickets.count()
        
        # Cartes de statistiques
        context['nb_projets'] = Project.objects.for_company(
            user.company_id).active().count()
        context['nb_tickets_actifs'] = tickets.exclude(
            status=TicketStatus.RESOLVED).count()
        context['nb_membres'] = user.company.members.count()

        # Cartes de projet, avec le nombre de tickets actifs de chacun
        context['projets'] = Project.objects.for_company(
            user.company_id).active().annotate(
            tickets_actifs=Count('tickets', filter=(
                Q(tickets__archived=False)
                & ~Q(tickets__status=TicketStatus.RESOLVED))))[:6]

        return context


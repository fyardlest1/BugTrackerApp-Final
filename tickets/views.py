# tickets/views.py
import os

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.views import View
from django.db.models import Q

from notifications.services import notify_many, notify

from .models import Ticket, TicketAttachment
from .forms import TicketForm, CommentForm
from .models import TicketStatus, TicketComment
from .services import assign_developer
from .filters import TicketFilter

from projects.models import Project
from accounts.permissions import can_edit_ticket, can_comment_ticket
from accounts.models import Roles



MAX_UPLOAD_SIZE = 5 * 1024 * 1024   # 5 Mo, exprimés en octets

ALLOWED_CONTENT_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf',
    # nouveau
    "text/csv", 
    "application/csv", 
    "application/vnd.ms-excel", 
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf',
    # nouveau
    '.csv', '.xls', '.xlsx', # '.doc', '.docx'
}


class TicketListView(LoginRequiredMixin, ListView):
    # 1. Configuration de base de la vue générique (ListView)
    # Spécifie le modèle, le template HTML, le nom de la variable dans le template, et active la pagination à 10 éléments par page
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        # 2. Initialisation et sécurisation par entreprise
        # Récupère l'utilisateur connecté et filtre immédiatement pour ne garder que les tickets non archivés de son entreprise
        user = self.request.user
        qs = Ticket.objects.filter(
            project__company=user.company, archived=False)

        # 3. Restriction des données selon le rôle de l'utilisateur
        if user.role == Roles.PROJECT_MANAGER:
            # Le chef de projet ne voit que les tickets des projets qu'il gère
            qs = qs.filter(project__manager=user)
        elif user.role != Roles.ADMIN:
            # Les autres rôles (développeurs/soumetteurs) ne voient que les tickets où ils sont impliqués directement
            qs = qs.filter(Q(developer=user) | Q(submitter=user))
        # (L'administrateur voit tout : aucun filtre supplémentaire n'est appliqué à son queryset)

        # 4. Application du formulaire de filtrage dynamique
        # Initialise le FilterSet avec les paramètres GET de l'URL et le queryset sécurisé, puis extrait le queryset filtré
        self.filterset = TicketFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        # 5. Enrichissement du contexte envoyé au template HTML
        # Récupère le contexte de base (qui inclut déjà la liste paginée des tickets) et y injecte le formulaire de filtre
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        return Ticket.objects.filter(
            project__company=self.request.user.company)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        project = self.object.project
        context['eligible_developers'] = project.members.filter(groups__name=Roles.DEVELOPER)
        context['can_edit'] = can_edit_ticket(self.request.user, self.object)

        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    success_url = reverse_lazy('tickets:list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['project'].queryset = Project.objects.for_company(
            self.request.user.company_id).active()
        return form

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        form.instance.status = TicketStatus.NEW
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'

    def get_queryset(self):
        return Ticket.objects.filter(
            project__company=self.request.user.company)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['project'].queryset = Project.objects.for_company(
            self.request.user.company_id).active()
        return form

    def get_success_url(self):
        return reverse_lazy('tickets:detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        return can_edit_ticket(self.request.user, self.get_object())
    
    def form_valid(self, form):
        # 1. On lit l'ancien statut AVANT l'enregistrement
        ancien = Ticket.objects.get(pk=self.object.pk).status
        # 2. On attribue le changement à son auteur (pour l'historique)
        form.instance._history_author = self.request.user
        # 3. On enregistre (déclenche save() et donc la journalisation)
        response = super().form_valid(form)
        # 4. On notifie si le ticket vient de passer à Résolu
        if (ancien != TicketStatus.RESOLVED
                and self.object.status == TicketStatus.RESOLVED):
            notify(self.object.submitter,
                f'Votre ticket a été résolu : {self.object.title}',
                reverse('tickets:detail', args=[self.object.pk]))
        return response


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(
            Ticket, pk=pk,
            project__company=request.user.company)
        
        if not can_comment_ticket(request.user, ticket):
            raise PermissionDenied

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            
            notify_many(
                [ticket.submitter, ticket.developer, ticket.project.manager],
                f'Nouveau commentaire sur : {ticket.title}',
                reverse('tickets:detail', args=[ticket.pk]),
                exclude=request.user)
        
        return redirect('tickets:detail', pk=pk)


class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(
            TicketComment, pk=pk, author=request.user)
        ticket_pk = comment.ticket.pk
        comment.delete()
        return redirect('tickets:detail', pk=ticket_pk)


class AddAttachmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(
            Ticket, pk=pk,
            project__company=request.user.company)
        
        if not can_comment_ticket(request.user, ticket):
            raise PermissionDenied

        upload = request.FILES.get('file')
        if upload:
            # 1. La taille
            if upload.size > MAX_UPLOAD_SIZE:
                messages.error(request, 'Le fichier dépasse la taille maximale de 5 Mo.')
                return redirect('tickets:detail', pk=pk)
            
            # 2. Le type déclaré
            if upload.content_type not in ALLOWED_CONTENT_TYPES:
                messages.error(
                    request, 'Type de fichier non autorisé. Formats acceptés : '
                            'images (JPEG, PNG, GIF, WebP), spreadsheet (XLS, XLSX, CSV) et PDF.')
                return redirect('tickets:detail', pk=pk)
            
            # 3. L'extension
            extension = os.path.splitext(upload.name)[1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                messages.error(request, 'Extension de fichier non autorisée.')
                return redirect('tickets:detail', pk=pk)
            
            TicketAttachment.objects.create(
                ticket=ticket,
                author=request.user,
                file=upload,
                file_name=upload.name,
                content_type=upload.content_type,
                description=request.POST.get('description', ''))
            
            notify_many(
                [ticket.submitter, ticket.developer, ticket.project.manager],
                f'Nouveau commentaire sur : {ticket.title}',
                reverse('tickets:detail', args=[ticket.pk]),
                exclude=request.user)

        return redirect('tickets:detail', pk=pk)


class DeleteAttachmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        attachment = get_object_or_404(
            TicketAttachment, pk=pk, author=request.user)
        ticket_pk = attachment.ticket.pk
        attachment.delete()
        return redirect('tickets:detail', pk=ticket_pk)


class AssignTicketView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ticket = get_object_or_404(
            Ticket, pk=pk,
            project__company=request.user.company)
        developer = get_object_or_404(
            get_user_model(), pk=request.POST['developer'],
            company=request.user.company)
        assign_developer(request.user, ticket, developer)
        return redirect('tickets:detail', pk=pk)


class MyTicketListView(LoginRequiredMixin, ListView):
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.filter(
            project__company=user.company, archived=False
        ).filter(Q(developer=user) | Q(submitter=user))

        self.filterset = TicketFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context



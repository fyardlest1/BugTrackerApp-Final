# api/views.py
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status as http_status

from projects.models import Project
from tickets.models import Ticket, TicketStatus, TicketComment, TicketAttachment
from notifications.services import notify_many, notify
from .serializers import (ProjectSerializer, TicketSerializer, 
                            CommentSerializer, AttachmentSerializer, 
                            MemberSerializer, CompanySerializer,
                        )
from .permissions import TicketPermission, ProjectPermission, CommentPermission
from tickets.services import assign_developer
from accounts.permissions import can_edit_ticket


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def get_queryset(self):
        return Project.objects.for_company(self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, TicketPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'project']

    def get_queryset(self):
        return Ticket.objects.filter(
            project__company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(submitter=self.request.user,
                        status=TicketStatus.NEW)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Liste les commentaires du ticket : /api/tickets/<id>/comments/"""
        ticket = self.get_object()
        data = CommentSerializer(
            ticket.comments.all(), many=True).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assigne un développeur : POST { \"developer\": <id> }"""
        ticket = self.get_object()
        developer = get_object_or_404(
            get_user_model(), pk=request.data.get('developer'),
            company=request.user.company)
        assign_developer(request.user, ticket, developer)
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Marque le ticket comme résolu : /api/tickets/<id>/resolve/"""
        ticket = self.get_object()
        if not can_edit_ticket(request.user, ticket):
            return Response(status=http_status.HTTP_403_FORBIDDEN)
        ticket.status = TicketStatus.RESOLVED
        ticket.save(update_fields=['status'])
        notify(ticket.submitter, f'Ton ticket a été résolu : {ticket.title}',
                reverse('tickets:detail', args=[ticket.pk]))
        return Response(TicketSerializer(ticket).data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, CommentPermission]

    def get_queryset(self):
        return TicketComment.objects.filter(
            ticket__project__company=self.request.user.company)

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        ticket = comment.ticket
        notify_many(
            [ticket.submitter, ticket.developer, ticket.project.manager],
            f'Nouveau commentaire sur : {ticket.title}',
            reverse('tickets:detail', args=[ticket.pk]),
            exclude=self.request.user)


class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return TicketAttachment.objects.filter(
            ticket__project__company=self.request.user.company)

    def perform_create(self, serializer):
        uploaded = self.request.data.get('file')
        serializer.save(
            author=self.request.user,
            file_name=getattr(uploaded, 'name', ''),
            content_type=getattr(uploaded, 'content_type', ''))


class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_user_model().objects.filter(
            company=self.request.user.company)


class CurrentCompanyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CompanySerializer(request.user.company)
        return Response(serializer.data)



# api/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.permissions import can_manage_project, can_comment_ticket, can_edit_ticket


class TicketPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Lecture : autorisée si le ticket est dans l'entreprise
        if request.method in SAFE_METHODS:
            return obj.project.company_id == request.user.company_id
        # Écriture : on réutilise notre règle métier
        return can_edit_ticket(request.user, obj)


class ProjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.company_id == request.user.company_id
        return can_manage_project(request.user, obj)


class CommentPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.ticket.project.company_id == request.user.company_id
        # On ne modifie ou ne supprime que ses propres commentaires
        return obj.author_id == request.user.id

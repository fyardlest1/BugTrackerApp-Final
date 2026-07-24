# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Company
from projects.models import Project
from tickets.models import Ticket, TicketComment, TicketAttachment


User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'manager', 'archived', 'created_at']
        read_only_fields = ['archived', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    submitter = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'priority',
                    'project', 'submitter', 'developer', 'created_at', 'updated_at']
        read_only_fields = ['submitter', 'status', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TicketComment
        fields = ['id', 'ticket', 'author', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']

    def validate_ticket(self, ticket):
        user = self.context['request'].user
        if ticket.project.company_id != user.company_id:
            raise serializers.ValidationError(
                "Ce ticket n'appartient pas à ton entreprise.")
        return ticket


class AttachmentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TicketAttachment
        fields = ['id', 'ticket', 'author', 'file', 'file_name',
                    'description', 'content_type', 'created_at']
        read_only_fields = ['author', 'file_name', 'content_type',
                            'created_at']

    def validate_ticket(self, ticket):
        user = self.context['request'].user
        if ticket.project.company_id != user.company_id:
            raise serializers.ValidationError(
                "Ce ticket n'appartient pas à ton entreprise.")
        return ticket


class MemberSerializer(serializers.ModelSerializer):
    role_label = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name',
                    'email', 'role_label']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description']


# api/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, TicketViewSet, CommentViewSet, 
    AttachmentViewSet, MemberViewSet, CurrentCompanyView
)


router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('comments', CommentViewSet, basename='comment')
router.register('attachments', AttachmentViewSet, basename='attachment')
router.register('members', MemberViewSet, basename='member')

urlpatterns = router.urls

urlpatterns = router.urls + [
    path('company/', CurrentCompanyView.as_view(), name='current-company'),
]

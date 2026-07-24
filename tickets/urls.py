# tickets/urls.py
from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='list'),
    path('nouveau/', views.TicketCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.TicketDetailView.as_view(), name='detail'),
    path('<uuid:pk>/modifier/', views.TicketUpdateView.as_view(), name='update'),
    path('<uuid:pk>/commentaires/', views.AddCommentView.as_view(), name='add_comment'),
    path('commentaires/<uuid:pk>/supprimer/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('<uuid:pk>/pieces-jointes/', views.AddAttachmentView.as_view(), name='add_attachment'),
    path('pieces-jointes/<uuid:pk>/supprimer/', views.DeleteAttachmentView.as_view(), name='delete_attachment'),
    path('<uuid:pk>/assigner/', views.AssignTicketView.as_view(), name='assign'),
    path('mes-tickets/', views.MyTicketListView.as_view(), name='my_tickets'),
    
]
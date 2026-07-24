# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('<uuid:pk>/lire/', views.ReadNotificationView.as_view(), name='read'),
]

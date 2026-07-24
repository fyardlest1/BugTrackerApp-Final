# notifications/views.py
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from .models import Notification


class ReadNotificationView(LoginRequiredMixin, View):
    def get(self, request, pk):
        notification = get_object_or_404(
            Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return redirect(notification.url or 'dashboard')

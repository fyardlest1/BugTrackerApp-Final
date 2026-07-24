# tickets/admin.py
from django.contrib import admin
from .models import Ticket, TicketComment, TicketAttachment


admin.site.register(Ticket)
admin.site.register(TicketComment)
admin.site.register(TicketAttachment)


# notifications/context_processors.py
def notifications(request):
    if not request.user.is_authenticated:
        return {}
    unread = request.user.notifications.filter(is_read=False)
    return {'unread_notifications': unread, 'unread_count': unread.count()}

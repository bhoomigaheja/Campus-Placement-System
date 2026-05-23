from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {
            'nav_notifications': unread[:10],
            'unread_notif_count': unread.count()
        }
    return {}

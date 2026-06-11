import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import threading
from .models import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_and_send(user, message, email_subject=None, email_template=None, context=None):
        """
        Centralized notification service that creates a database Notification
        and synchronously sends an email. Designed to be future-ready for Celery/Redis.
        """
        try:
            notification = Notification.objects.create(user=user, message=message)
        except Exception as e:
            logger.error(f"Failed to create notification for {user}: {e}")
            notification = None

        # 2. Send Email if subject is provided
        if email_subject and user.email:
            def _send_company_email():
                try:
                    if email_template and context:
                        # Attempt HTML email rendering
                        from django.template.loader import render_to_string
                        from django.utils.html import strip_tags
                        html_message = render_to_string(email_template, context)
                        plain_message = strip_tags(html_message)
                    else:
                        html_message = None
                        plain_message = message

                    send_mail(
                        subject=f"CampusConnect: {email_subject}",
                        message=plain_message,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@campusconnect.com'),
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=True
                    )
                    logger.info(f"Email sent successfully to {user.email} for: {email_subject}")
                except Exception as e:
                    logger.error(f"Failed to send email to {user.email}: {e}")
            
            import threading
            threading.Thread(target=_send_company_email, daemon=True).start()

        return notification

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
                        subject=f"CareerConnect: {email_subject}",
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

class EmailService:
    @staticmethod
    def _send_email(subject, template_name, context, recipient_list):
        if not isinstance(recipient_list, list):
            recipient_list = [recipient_list]
            
        def _send():
            try:
                html_message = render_to_string(template_name, context)
                plain_message = strip_tags(html_message)
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@careerconnect.com')
                
                # Fetch all TPO emails
                from accounts.models import User
                tpo_emails = list(User.objects.filter(is_admin=True).values_list('email', flat=True))
                
                from django.core.mail import EmailMultiAlternatives
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=from_email,
                    to=recipient_list,
                    bcc=tpo_emails
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=False)
                
                logger.info(f"Email sent successfully to {recipient_list} (BCC: {tpo_emails}) for: {subject}")
            except Exception as e:
                logger.error(f"Error preparing/sending email {template_name} to {recipient_list}: {str(e)}")

        import threading
        threading.Thread(target=_send, daemon=True).start()
        return True

    @staticmethod
    def send_welcome_email(user, verification_link, is_student=True, is_company=False, temp_password=None):
        context = {
            'user': user,
            'verification_link': verification_link,
            'is_student': is_student,
            'is_company': is_company,
            'temp_password': temp_password,
        }
        return EmailService._send_email(
            "Welcome to CareerConnect - Verify Your Account",
            "emails/welcome_email.html",
            context,
            user.email
        )

    @staticmethod
    def send_password_reset(user, reset_link):
        context = {
            'user': user,
            'reset_link': reset_link
        }
        return EmailService._send_email(
            "CareerConnect - Password Reset Request",
            "emails/password_reset.html",
            context,
            user.email
        )

    @staticmethod
    def send_application_received(application):
        context = {'application': application, 'student': application.student.user}
        return EmailService._send_email(
            f"Application Received: {application.job.company.company_name}",
            "emails/application_received.html",
            context,
            application.student.user.email
        )

    @staticmethod
    def send_status_update(application):
        context = {'application': application, 'student': application.student.user}
        subject = f"Application Update: {application.job.company.company_name}"
        return EmailService._send_email(
            subject,
            "emails/status_update.html",
            context,
            application.student.user.email
        )

    @staticmethod
    def send_interview_scheduled(interview, recipient_email, is_student=True):
        context = {'interview': interview, 'is_student': is_student, 'domain': getattr(settings, 'SITE_URL', 'http://localhost:8000')}
        subject = f"Interview Scheduled: {interview.application.job.company.company_name}"
        return EmailService._send_email(
            subject,
            "emails/interview_scheduled.html",
            context,
            recipient_email
        )

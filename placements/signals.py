from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application
from .tasks import send_email_task, parse_resume_and_score_task

@receiver(post_save, sender=Application)
def application_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            # Trigger parsing and matching
            parse_resume_and_score_task.delay(instance.id)
            
            # Send confirmation email
            message = f"Hello {instance.student.user.email}, your application for {instance.job.title} was received."
            send_email_task.delay("Application Received", message, [instance.student.user.email])
        else:
            # Check specific status transitions
            if instance.status == 'SHORTLISTED':
                msg = f"Congratulations! You've been shortlisted for {instance.job.title}."
                send_email_task.delay("Application Update", msg, [instance.student.user.email])
    except Exception as e:
        import traceback
        print(f"SIGNAL CRASH: {e}\n{traceback.format_exc()}")

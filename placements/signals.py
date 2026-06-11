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
            
            # Send confirmation email is now handled in ApplicationService
            pass
        else:
            # Status updates are handled in ApplicationService
            pass
    except Exception as e:
        import traceback
        print(f"SIGNAL CRASH: {e}\n{traceback.format_exc()}")

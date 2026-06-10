from celery import shared_task
from django.core.mail import send_mail
from .models import Application
from .ml_services import calculate_resume_match

import threading

@shared_task
def send_email_task(subject, message, recipient_list):
    def _send_async():
        send_mail(
            subject,
            message,
            'noreply@campusplacement.com',
            recipient_list,
            fail_silently=True,
        )
    threading.Thread(target=_send_async, daemon=True).start()
    return f"Email dispatch initiated for {recipient_list}"

@shared_task
def parse_resume_and_score_task(application_id):
    try:
        app = Application.objects.select_related('student', 'job').get(id=application_id)
        
        student_skills_qs = app.student.skills.all()
        job_skills_qs = app.job.required_skills.all()
        
        student_skills_str = " ".join([s.name for s in student_skills_qs])
        job_skills_str = " ".join([s.name for s in job_skills_qs])
        
        score = calculate_resume_match(student_skills_str, job_skills_str)
        app.match_score = score
        app.save(update_fields=['match_score'])
        return f"Scored App {application_id}: {score}%"
    except Application.DoesNotExist:
        return "Application not found."

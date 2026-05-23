from celery import shared_task
from django.core.mail import send_mail
from .models import Application
from .ml_services import calculate_resume_match

@shared_task
def send_email_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'noreply@campusplacement.com',
        recipient_list,
        fail_silently=False,
    )
    return f"Email sent to {recipient_list}"

@shared_task
def parse_resume_and_score_task(application_id):
    try:
        app = Application.objects.select_related('student', 'job').get(id=application_id)
        student_skills = app.student.skills
        job_skills = app.job.skills_required
        
        score = calculate_resume_match(student_skills, job_skills)
        app.match_score = score
        app.save(update_fields=['match_score'])
        return f"Scored App {application_id}: {score}%"
    except Application.DoesNotExist:
        return "Application not found."

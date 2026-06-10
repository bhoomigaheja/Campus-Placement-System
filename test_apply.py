import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from placements.models import Job, Application
from accounts.models import StudentProfile, User
from placements.services.application_services import ApplicationService

student_user = User.objects.filter(is_student=True).first()
if not student_user:
    print("No student user found.")
    exit(1)

student_profile = getattr(student_user, 'student_profile', None)
if not student_profile:
    print("Student user has no profile.")
    exit(1)

# Ensure student has branch, cgpa, resume, skills
from students.models import Branch, Skill
if not student_profile.branch:
    student_profile.branch = Branch.objects.first()
if not student_profile.cgpa:
    student_profile.cgpa = 8.5
if not student_profile.resume:
    student_profile.resume = 'resumes/dummy.pdf'
student_profile.save()
student_profile.skills.add(Skill.objects.first())

job = Job.objects.first()
if not job:
    print("No jobs found.")
    exit(1)

# Delete existing application to allow applying again
Application.objects.filter(student=student_profile, job=job).delete()

print(f"Applying to job {job.title} with student {student_profile.user.email}...")
try:
    application = ApplicationService.apply_to_job(student_profile, job)
    print("Success!", application)
except Exception as e:
    import traceback
    traceback.print_exc()

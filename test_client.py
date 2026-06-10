import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from django.test import Client
from placements.models import Job, Application
from accounts.models import User

client = Client()

student_user = User.objects.filter(is_student=True).first()
if not student_user:
    print("No student user found.")
    exit(1)

# forcefully reset password to login easily
student_user.set_password('password123')
student_user.save()

client.login(email=student_user.email, password='password123')

job = Job.objects.first()
# clean previous app
Application.objects.filter(student=student_user.student_profile, job=job).delete()

# get the CSRF token
response = client.get(f'/student/drives/{job.id}/')
print("Detail GET status:", response.status_code)

# post to apply
apply_url = f'/tpo/student/drives/{job.id}/apply/'
response = client.post(apply_url)
print("Apply POST status:", response.status_code)
if response.status_code == 500:
    print(response.content.decode('utf-8'))

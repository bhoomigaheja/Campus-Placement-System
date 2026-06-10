import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from django.test import Client
from accounts.models import User
from students.models import Branch

client = Client()

student_user = User.objects.filter(is_student=True).first()
if not student_user:
    print("No student user found.")
    exit(1)

student_user.set_password('password123')
student_user.save()

client.login(email=student_user.email, password='password123')

branch = Branch.objects.first()

data = {
    'phone_number': '1234567890',
    'enrollment_number': 'ENR123',
    'branch': branch.id if branch else '',
    'cgpa': '8.5',
    'bio': 'Test bio'
}

print(f"Testing profile update for {student_user.email}")
try:
    response = client.post('/students/profile/update/', data, follow=True)
    print("Status:", response.status_code)
    if response.status_code == 500:
        print("Crash!")
except Exception as e:
    import traceback
    traceback.print_exc()

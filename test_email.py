import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail('Test Subject', 'Test Message', 'noreply@campusconnect.com', ['test@example.com'], fail_silently=False)
    print('Success')
except Exception as e:
    print('Error:', e)

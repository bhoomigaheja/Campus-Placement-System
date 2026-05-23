import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

client = Client()
User = get_user_model()
try:
    user = User.objects.create_superuser('testadmin99@example.com', 'admin_pass')
except Exception as e:
    user = User.objects.get(email='testadmin99@example.com')

client.force_login(user)

routes_to_test = [
    '/dashboard/',
    '/tpo/dashboard/',
    '/tpo/companies/',
    '/tpo/companies/add/',
    '/tpo/drives/',
    '/tpo/drives/add/',
]

for route in routes_to_test:
    try:
        response = client.get(route)
        print(f"PASS: GET {route} -> Status: {response.status_code}")
    except Exception as e:
        print(f"FAIL: GET {route} -> Exception: {str(e)}")

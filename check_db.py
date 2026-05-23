import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from students.models import Branch, Skill
print(f"Branches: {Branch.objects.count()}")
print(f"Skills: {Skill.objects.count()}")

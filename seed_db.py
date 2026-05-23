import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from students.models import Branch, Skill

# Create default branches
branches = [
    {"name": "Computer Science and Engineering", "code": "CSE"},
    {"name": "Information Technology", "code": "IT"},
    {"name": "Electronics and Communication Engineering", "code": "ECE"},
    {"name": "Electrical Engineering", "code": "EE"},
    {"name": "Mechanical Engineering", "code": "ME"},
    {"name": "Civil Engineering", "code": "CE"},
    {"name": "Master of Computer Applications", "code": "MCA"},
    {"name": "Master of Business Administration", "code": "MBA"}
]

for branch_data in branches:
    Branch.objects.get_or_create(name=branch_data["name"], defaults={"code": branch_data["code"]})

print("Default branches added successfully!")

# Create default skills (Skills usually don't have constraints like code)
skills = [
    "Python", "Java", "C++", "JavaScript", "HTML/CSS", 
    "React", "Angular", "Node.js", "Django", "Flask",
    "SQL", "MongoDB", "AWS", "Docker", "Git",
    "Machine Learning", "Data Analysis", "Cloud Computing"
]

for skill_name in skills:
    Skill.objects.get_or_create(name=skill_name)
    
print("Default skills added successfully!")

import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from accounts.models import User, StudentProfile
from students.models import Branch, Skill
from placements.models import Job, Application
from placements.signals import application_post_save
from django.db.models.signals import post_save

def create_and_apply_students():
    print("Starting to create 4 realistic students...")

    # Disconnect the signal so Celery doesn't crash on missing resumes
    post_save.disconnect(application_post_save, sender=Application)

    try:
        microsoft_job = Job.objects.filter(company__company_name__icontains='Microsoft').first()
        if not microsoft_job:
            return "Microsoft job drive not found!"

        try:
            branch_cse = Branch.objects.get(code="CSE")
            skill_python = Skill.objects.get(name="Python")
            skill_aws = Skill.objects.get(name="AWS")
        except:
            return "Run /init-tpo/ first to populate base data."

        students_data = [
            {"email": "rahul.sharma@college.edu", "first": "Rahul", "last": "Sharma", "cgpa": 9.2, "score": 92.5},
            {"email": "priya.singh@college.edu", "first": "Priya", "last": "Singh", "cgpa": 8.8, "score": 85.0},
            {"email": "amit.patel@college.edu", "first": "Amit", "last": "Patel", "cgpa": 7.9, "score": 78.2},
            {"email": "sneha.gupta@college.edu", "first": "Sneha", "last": "Gupta", "cgpa": 9.5, "score": 96.0},
        ]

        count = 1
        msg = "<h3>Students Created & Applied:</h3><ul>"
        for data in students_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    'first_name': data["first"],
                    'last_name': data["last"],
                    'is_student': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()

                profile = StudentProfile.objects.create(
                    user=user,
                    enrollment_number=f"ENR2026{count:03d}",
                    phone_number=f"987654321{count}",
                    cgpa=data["cgpa"],
                    branch=branch_cse,
                    projects="Built a scalable E-commerce backend using Django and AWS.",
                    internships="SDE Intern at TechCorp for 3 months."
                )
                profile.skills.add(skill_python, skill_aws)
                
                # Apply to Microsoft
                Application.objects.create(
                    job=microsoft_job,
                    student=profile,
                    status='APPLIED',
                    match_score=data["score"]
                )
                msg += f"<li>{data['first']} {data['last']} applied with ATS Score {data['score']}%</li>"
            else:
                msg += f"<li>{data['first']} {data['last']} already exists.</li>"
            count += 1
            
        msg += "</ul><p>✅ <strong>4 Realistic students successfully created and applied to Microsoft!</strong></p>"
        return msg
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Reconnect the signal
        post_save.connect(application_post_save, sender=Application)

if __name__ == "__main__":
    print(create_and_apply_students())

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from accounts.models import User, StudentProfile, CompanyProfile
from students.models import Branch, Skill
from placements.models import Job
from django.utils import timezone
from datetime import timedelta

def create_dummy_data():
    print("Starting to create dummy data...")

    # 1. Ensure a Branch and Skills exist
    branch, _ = Branch.objects.get_or_create(name="Computer Science and Engineering", defaults={"code": "CSE"})
    skill_python, _ = Skill.objects.get_or_create(name="Python")
    skill_django, _ = Skill.objects.get_or_create(name="Django")
    print("Branches and Skills ensured.")

    # 2. Create TPO (Admin)
    if not User.objects.filter(email='vg199r@gmail.com').exists():
        tpo = User.objects.create_user(
            email='vg199r@gmail.com',
            password='password123',
            is_admin=True,
            first_name='Admin',
            last_name='TPO'
        )
        print("Created TPO user: vg199r@gmail.com (password: password123)")
    else:
        print("TPO user already exists.")

    # 3. Create Student
    if not User.objects.filter(email='student@college.edu').exists():
        student_user = User.objects.create_user(
            email='student@college.edu',
            password='password123',
            first_name='John',
            last_name='Doe',
            is_student=True
        )
        profile = StudentProfile.objects.create(
            user=student_user,
            cgpa=8.5,
            branch=branch,
            resume='resumes/dummy_resume.pdf'  # Fake path just to pass validation if needed later
        )
        profile.skills.add(skill_python, skill_django)
        print("Created Student user: student@college.edu (password: password123)")
    else:
        print("Student user already exists.")

    # 4. Create Company
    if not User.objects.filter(email='hr@techcorp.com').exists():
        company_user = User.objects.create_user(
            email='hr@techcorp.com',
            password='password123',
            first_name='Tech',
            last_name='Corp HR',
            is_company=True
        )
        company_profile = CompanyProfile.objects.create(
            user=company_user,
            company_name='TechCorp Innovations',
            industry='Software',
            website='https://techcorp.example.com'
        )
        print("Created Company user: hr@techcorp.com (password: password123)")
        
        # 5. Create a Job Drive
        if not Job.objects.filter(title='Software Engineer').exists():
            tpo_user = User.objects.filter(email='vg199r@gmail.com').first()
            job = Job.objects.create(
                company=company_profile,
                title='Software Engineer',
                description='Looking for full-stack developers.',
                min_cgpa=7.0,
                salary_package='12 LPA',
                deadline_to_apply=timezone.now() + timedelta(days=7),
                status='APPROVED',
                created_by=tpo_user,
                approved_by=tpo_user,
                approval_timestamp=timezone.now()
            )
            job.eligible_branches.add(branch)
            job.required_skills.add(skill_python, skill_django)
            print("Created Job Drive: Software Engineer at TechCorp Innovations")

    else:
        print("Company user already exists.")

    print("Dummy data creation complete!")

if __name__ == "__main__":
    create_dummy_data()

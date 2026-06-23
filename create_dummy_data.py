import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from accounts.models import User, StudentProfile, CompanyProfile
from students.models import Branch, Skill
from placements.models import Job

def create_realistic_data():
    print("Starting to create realistic company and job data...")

    # 1. Ensure Branches and Skills
    branch_cse, _ = Branch.objects.get_or_create(name="Computer Science and Engineering", defaults={"code": "CSE"})
    branch_it, _ = Branch.objects.get_or_create(name="Information Technology", defaults={"code": "IT"})
    branch_ece, _ = Branch.objects.get_or_create(name="Electronics", defaults={"code": "ECE"})
    
    skill_python, _ = Skill.objects.get_or_create(name="Python")
    skill_django, _ = Skill.objects.get_or_create(name="Django")
    skill_java, _ = Skill.objects.get_or_create(name="Java")
    skill_react, _ = Skill.objects.get_or_create(name="React")
    skill_aws, _ = Skill.objects.get_or_create(name="AWS")
    
    print("Branches and Skills verified.")

    # 2. Get TPO Admin
    tpo_user = User.objects.filter(is_admin=True).first()
    if not tpo_user:
        print("TPO user not found. Run /init-tpo/ first!")
        return

    # Realistic Companies Data
    companies_data = [
        {
            "email": "hr@google.com",
            "name": "Google",
            "industry": "Technology",
            "website": "https://careers.google.com",
            "tier": "Tier 1",
            "desc": "Google LLC is an American multinational technology company focusing on search engine technology, online advertising, cloud computing, computer software, quantum computing, e-commerce, artificial intelligence, and consumer electronics.",
            "job_title": "Software Engineer (SDE I)",
            "job_desc": "We are looking for passionate Software Engineers to build scalable systems. You will work on cutting-edge technologies and impact billions of users worldwide. Experience with algorithms and distributed systems is a plus.",
            "salary": "24 LPA",
            "cgpa": 8.0,
            "skills": [skill_python, skill_java],
            "branches": [branch_cse, branch_it]
        },
        {
            "email": "careers@microsoft.com",
            "name": "Microsoft",
            "industry": "Software",
            "website": "https://careers.microsoft.com",
            "tier": "Tier 1",
            "desc": "Microsoft Corporation is an American multinational technology corporation which produces computer software, consumer electronics, personal computers, and related services.",
            "job_title": "Cloud Architect",
            "job_desc": "Join the Azure team to build the future of cloud computing. You will be responsible for designing and deploying highly scalable cloud infrastructure.",
            "salary": "45 LPA",
            "cgpa": 8.5,
            "skills": [skill_aws, skill_python],
            "branches": [branch_cse, branch_it, branch_ece]
        },
        {
            "email": "hiring@tcs.com",
            "name": "Tata Consultancy Services (TCS)",
            "industry": "IT Services",
            "website": "https://www.tcs.com",
            "tier": "Mass Recruiter",
            "desc": "Tata Consultancy Services is an Indian multinational information technology services and consulting company.",
            "job_title": "System Engineer (Ninja)",
            "job_desc": "Looking for freshers to join our IT consulting teams. Good problem solving skills and basic programming knowledge is required.",
            "salary": "3.36 LPA",
            "cgpa": 6.0,
            "skills": [skill_java],
            "branches": [branch_cse, branch_it, branch_ece]
        },
        {
            "email": "recruitment@amazon.in",
            "name": "Amazon",
            "industry": "E-Commerce / Tech",
            "website": "https://amazon.jobs",
            "tier": "Tier 1",
            "desc": "Amazon.com, Inc. is an American multinational technology company focusing on e-commerce, cloud computing, online advertising, digital streaming, and artificial intelligence.",
            "job_title": "Frontend Developer",
            "job_desc": "Looking for strong frontend engineers who can build responsive and performant user interfaces for our global e-commerce platform.",
            "salary": "18 LPA",
            "cgpa": 7.5,
            "skills": [skill_react, skill_django],
            "branches": [branch_cse, branch_it]
        }
    ]

    for data in companies_data:
        # Create or Get Company User
        company_user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                'first_name': data["name"].split()[0],
                'last_name': 'HR',
                'is_company': True
            }
        )
        if created:
            company_user.set_password('password123')
            company_user.save()
            
            CompanyProfile.objects.create(
                user=company_user,
                company_name=data["name"],
                industry=data["industry"],
                website=data["website"],
                tier=data["tier"],
                description=data["desc"]
            )
            print(f"Created Company: {data['name']}")
        
        profile = company_user.company_profile

        # Create Job Drive
        job, job_created = Job.objects.get_or_create(
            company=profile,
            title=data["job_title"],
            defaults={
                'description': data["job_desc"],
                'min_cgpa': data["cgpa"],
                'salary_package': data["salary"],
                'deadline_to_apply': timezone.now() + timedelta(days=14),
                'location': 'Bangalore, India',
                'employment_type': 'Full-time',
                'status': 'APPROVED',
                'created_by': tpo_user,
                'approved_by': tpo_user,
                'approval_timestamp': timezone.now()
            }
        )
        if job_created:
            job.eligible_branches.add(*data["branches"])
            job.required_skills.add(*data["skills"])
            print(f"Created Job Drive: {data['job_title']} at {data['name']}")

    print("\n✅ Awesome! Realistic Dummy Data successfully loaded.")

if __name__ == "__main__":
    create_realistic_data()

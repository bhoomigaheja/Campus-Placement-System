from django.db import models
from django.conf import settings
from accounts.models import CompanyProfile, StudentProfile
from students.models import Branch, Skill

class Job(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill, blank=True)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    eligible_branches = models.ManyToManyField(Branch, blank=True)
    salary_package = models.CharField(max_length=100, blank=True)
    deadline_to_apply = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True, default='On-site')
    employment_type = models.CharField(max_length=100, blank=True, null=True, default='Full-time')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Workflow and Audit logs
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_jobs')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_jobs')
    approval_timestamp = models.DateTimeField(null=True, blank=True)
    rejection_remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

class Application(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview'),
        ('OFFERED', 'Offered'),
        ('REJECTED', 'Rejected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    match_score = models.FloatField(default=0.0, help_text="AI match score percentage")
    remarks = models.TextField(blank=True, null=True, help_text="Recruiter remarks or feedback")
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.email} -> {self.job.title} ({self.status})"

class Interview(models.Model):
    MODE_CHOICES = [
        ('ONLINE', 'Online'),
        ('IN_PERSON', 'In-Person'),
    ]
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview')
    scheduled_at = models.DateTimeField()
    interview_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='ONLINE')
    meeting_link = models.CharField(max_length=255, blank=True, null=True, help_text="Online meeting URL or physical venue location")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Interview for {self.application}"

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from students.models import Skill, Branch
from core.validators import validate_file_extension, validate_file_size
from core.utils.media_utils import MediaHelper

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    is_student = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    # skills = models.TextField(help_text="Comma separated skills, e.g., Python, Django, React")
    skills = models.ManyToManyField(Skill, blank=True)
    resume = models.FileField(
        upload_to='resumes/', 
        null=True, 
        blank=True,
        validators=[validate_file_extension, validate_file_size]
    )
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    projects = models.TextField(blank=True)
    internships = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.enrollment_number:
            self.enrollment_number = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - Profile"

class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    tier = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.company_name

@receiver(post_delete, sender=StudentProfile)
def auto_delete_resume_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `StudentProfile` object is deleted."""
    if instance.resume:
        MediaHelper.safe_delete(instance.resume)

@receiver(pre_save, sender=StudentProfile)
def auto_delete_resume_on_change(sender, instance, **kwargs):
    """Deletes old file from filesystem when corresponding `StudentProfile` object is updated with new file."""
    if not instance.pk:
        return False

    try:
        old_profile = StudentProfile.objects.get(pk=instance.pk)
    except StudentProfile.DoesNotExist:
        return False

    old_resume = old_profile.resume
    new_resume = instance.resume

    if not old_resume == new_resume:
        MediaHelper.safe_delete(old_resume)

from django.db import IntegrityError
from placements.models import Application
from core.models import Notification

class ApplicationService:
    @staticmethod
    def check_eligibility(student_profile, job):
        if not student_profile.branch:
            return False, "Please update your profile with your branch first."
        if student_profile.cgpa is None:
            return False, "Please update your profile with your CGPA first."
        if not student_profile.resume:
            return False, "Please upload your resume before applying."
        if not student_profile.skills.exists():
            return False, "Please add at least one skill to your profile."

        if student_profile.cgpa < job.min_cgpa:
            return False, "CGPA is below the minimum requirement."

        if job.eligible_branches.exists() and not job.eligible_branches.filter(id=student_profile.branch.id).exists():
            return False, "Your branch is not eligible for this drive."

        # Could add required_skills checks here if strict matching is needed
        # For now, we allow applying if basic constraints meet
        return True, None

    @staticmethod
    def apply_to_job(student_profile, job):
        is_eligible, reason = ApplicationService.check_eligibility(student_profile, job)
        if not is_eligible:
            raise ValueError(reason)

        try:
            application = Application.objects.create(student=student_profile, job=job)
            
            # Notify company
            Notification.objects.create(
                user=job.company.user,
                message=f"New candidate '{student_profile.user.first_name}' has applied securely for position '{job.title}'"
            )
            return application
        except IntegrityError:
            raise ValueError("You have already applied to this drive.")

    @staticmethod
    def update_application_status(application, new_status, remarks=None, updated_by_role='Employer'):
        application.status = new_status
        if remarks:
            application.remarks = remarks
        application.save()

        Notification.objects.create(
            user=application.student.user,
            message=f"{updated_by_role} updated your status for '{application.job.title}' to '{application.get_status_display()}'."
        )
        return application

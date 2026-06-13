from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from core.mixins import StudentRequiredMixin
from accounts.models import StudentProfile
from placements.models import Application
from .forms import StudentProfileForm

class StudentDashboardView(LoginRequiredMixin, StudentRequiredMixin, TemplateView):
    template_name = 'students/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'student_profile'):
            profile = self.request.user.student_profile
            context['profile'] = profile
            
            apps = Application.objects.filter(student=profile)
            context['total_applications'] = apps.count()
            context['shortlisted_count'] = apps.filter(status='SHORTLISTED').count()
            context['offered_count'] = apps.filter(status='OFFERED').count()
            
            # Journey Tracker data
            context['latest_application'] = apps.order_by('-applied_at').first()
            
            # Recommended Drives (just active drives not yet applied to)
            from placements.models import Job
            applied_job_ids = apps.values_list('job_id', flat=True)
            context['recommended_drives'] = Job.objects.filter(status='APPROVED').exclude(id__in=applied_job_ids).order_by('deadline_to_apply')[:3]
            
        return context

class StudentProfileUpdateView(LoginRequiredMixin, StudentRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'students/profile_update.html'
    success_url = reverse_lazy('student_dashboard')
    
    def get_object(self, queryset=None):
        profile, created = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Resume profile and credentials successfully updated!")
        return super().form_valid(form)

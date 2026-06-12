from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from core.mixins import StudentRequiredMixin
# TPORequiredMixin was modified to check is_admin perfectly.
from core.mixins import TPORequiredMixin
from accounts.models import StudentProfile, CompanyProfile
from accounts.models import StudentProfile, CompanyProfile
from .models import Job, Application, Interview
from .forms import CompanyForm, JobForm, CompanyJobForm, ApplicationStatusForm, InterviewForm, CompanyApplicationUpdateForm, TPOCompanyEditForm
from core.services import NotificationService
from placements.services.company_services import CompanyService
from placements.services.application_services import ApplicationService
from placements.services.analytics_services import AnalyticsService

class TPODashboardView(LoginRequiredMixin, TPORequiredMixin, TemplateView):
    template_name = 'placements/tpo_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = AnalyticsService.get_tpo_dashboard_stats()
        context.update(stats)
        
        context['recent_drives'] = Job.objects.select_related('company').order_by('-created_at')[:5]
        return context

class CompanyListView(LoginRequiredMixin, TPORequiredMixin, ListView):
    model = CompanyProfile
    template_name = 'placements/tpo_company_list.html'
    context_object_name = 'companies'

from accounts.models import User

class CompanyCreateView(LoginRequiredMixin, TPORequiredMixin, CreateView):
    model = CompanyProfile
    form_class = CompanyForm
    template_name = 'placements/tpo_company_form.html'
    success_url = reverse_lazy('tpo_company_list')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        company_name = form.cleaned_data.get('company_name')
        website = form.cleaned_data.get('website', '')
        industry = form.cleaned_data.get('industry', '')
        try:
            company = CompanyService.create_company(email, password, company_name, website, industry)
            form.instance = company
            
            # Send notification for Company Registration
            msg = f"Your company '{company_name}' has been successfully registered on CareerConnect. You can now log in and post job drives."
            NotificationService.create_and_send(
                user=company.user,
                message=msg,
                email_subject="Company Registered Successfully",
                email_template="emails/base_notification.html",
                context={'title': 'Welcome to CareerConnect', 'message': msg, 'action_url': '#'}
            )
        except ValueError as e:
            form.add_error('email', str(e))
            return self.form_invalid(form)
        return super().form_valid(form)

class DriveListView(LoginRequiredMixin, TPORequiredMixin, ListView):
    model = Job
    template_name = 'placements/tpo_drive_list.html'
    context_object_name = 'drives'
    ordering = ['-created_at']

class DriveCreateView(LoginRequiredMixin, TPORequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'placements/tpo_drive_form.html'
    success_url = reverse_lazy('tpo_drive_list')

    def form_valid(self, form):
        company_name = form.cleaned_data['company_name']
        company = CompanyProfile.objects.get(company_name=company_name)
        form.instance.company = company
        response = super().form_valid(form)
        
        job = self.object
        messages.success(self.request, f"Placement drive for '{job.title}' created successfully!")
        
        return response

class DriveUpdateView(LoginRequiredMixin, TPORequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'placements/tpo_drive_form.html'
    success_url = reverse_lazy('tpo_drive_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        company_name = form.cleaned_data['company_name']
        company = CompanyProfile.objects.get(company_name=company_name)
        form.instance.company = company
        messages.success(self.request, f"Placement drive for '{form.cleaned_data.get('title')}' successfully updated!")
        return super().form_valid(form)

class DriveDeleteView(LoginRequiredMixin, TPORequiredMixin, View):
    def post(self, request, pk):
        drive = get_object_or_404(Job, pk=pk)
        title = drive.title
        company = drive.company.company_name
        drive.delete()
        messages.success(request, f"Drive for '{title}' at '{company}' successfully deleted.")
        return redirect('tpo_drive_list')

from django.views.generic import DeleteView

class CompanyUpdateView(LoginRequiredMixin, TPORequiredMixin, UpdateView):
    model = CompanyProfile
    template_name = 'placements/tpo_company_edit.html'
    form_class = TPOCompanyEditForm
    success_url = reverse_lazy('tpo_company_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.object.user
        return kwargs

    def form_valid(self, form):
        # Update User model
        user = self.object.user
        user.email = form.cleaned_data.get('email')
        
        contact_person = form.cleaned_data.get('contact_person', '')
        if contact_person:
            parts = contact_person.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            else:
                user.last_name = ''
                
        new_password = form.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
            
        user.save()
        
        messages.success(self.request, f"Company '{form.cleaned_data.get('company_name')}' successfully updated!")
        return super().form_valid(form)

class CompanyDeleteView(LoginRequiredMixin, TPORequiredMixin, DeleteView):
    model = CompanyProfile
    template_name = 'placements/tpo_company_confirm_delete.html'
    success_url = reverse_lazy('tpo_company_list')
    context_object_name = 'company'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Company and all associated jobs/applications successfully deleted.")
        return super().delete(request, *args, **kwargs)

class DriveDetailView(LoginRequiredMixin, TPORequiredMixin, DetailView):
    model = Job
    template_name = 'placements/tpo_drive_detail.html'
    context_object_name = 'drive'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = self.object.applications.all().select_related('student__user')
        return context

class ApplicationStatusUpdateView(LoginRequiredMixin, TPORequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationStatusForm
    template_name = 'placements/tpo_application_update.html'
    
    def get_success_url(self):
        ApplicationService.update_application_status(
            self.object, 
            self.object.status, 
            updated_by_role='TPO'
        )
        return reverse('tpo_drive_detail', kwargs={'pk': self.object.job.pk})

class InterviewScheduleCreateView(LoginRequiredMixin, TPORequiredMixin, CreateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'placements/tpo_interview_form.html'
    
    def form_valid(self, form):
        form.instance.application = get_object_or_404(Application, pk=self.kwargs['app_pk'])
        response = super().form_valid(form)
        msg = f"Interview formally scheduled for {self.object.application.job.title} on {self.object.scheduled_at.strftime('%Y-%m-%d %H:%M')}."
        NotificationService.create_and_send(
            user=self.object.application.student.user,
            message=msg,
            email_subject="Interview Scheduled",
            email_template="emails/interview_scheduled.html",
            context={
                'student_name': self.object.application.student.user.first_name,
                'job_title': self.object.application.job.title,
                'company_name': self.object.application.job.company.company_name,
                'scheduled_at': self.object.scheduled_at.strftime('%Y-%m-%d %H:%M'),
                'mode': "Online" if self.object.mode == 'ONLINE' else "In-Person",
                'link': self.object.location_link,
                'notes': self.object.notes,
            }
        )
        return response
        
    def get_success_url(self):
        return reverse('tpo_drive_detail', kwargs={'pk': self.object.application.job.pk})

class StudentDriveListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Job
    template_name = 'placements/student_drive_list.html'
    context_object_name = 'drives'
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'student_profile'):
            applied_drive_ids = Application.objects.filter(
                student=self.request.user.student_profile
            ).values_list('job_id', flat=True)
            context['applied_drive_ids'] = applied_drive_ids
        return context

class StudentDriveDetailView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = Job
    template_name = 'placements/student_drive_detail.html'
    context_object_name = 'drive'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'student_profile'):
            profile = self.request.user.student_profile
            context['has_applied'] = Application.objects.filter(student=profile, job=self.object).exists()
            
            is_eligible, reason = ApplicationService.check_eligibility(profile, self.object)
            context['is_eligible'] = is_eligible
            context['ineligibility_reason'] = reason if not is_eligible else ""
            
        return context

class ApplyDriveView(LoginRequiredMixin, StudentRequiredMixin, View):
    def get(self, request, pk):
        return redirect('student_drive_detail', pk=pk)

    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        
        if not hasattr(request.user, 'student_profile'):
            messages.error(request, 'Please complete your profile first.')
            return redirect('student_profile_update')
            
        profile = request.user.student_profile
        
        try:
            ApplicationService.apply_to_job(profile, job)
            messages.success(request, 'Successfully applied to the drive!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            import traceback
            messages.error(request, f"CRITICAL ERROR: {str(e)}")
            print(f"APPLY CRASH: {traceback.format_exc()}")
            
        return redirect('student_drive_detail', pk=pk)

class StudentApplicationsListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Application
    template_name = 'placements/student_applications.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return Application.objects.filter(student=self.request.user.student_profile).select_related('job__company')
        return Application.objects.none()

from core.mixins import CompanyRequiredMixin

class CompanyDashboardView(LoginRequiredMixin, CompanyRequiredMixin, TemplateView):
    template_name = 'placements/company_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'company_profile'):
            profile = self.request.user.company_profile
            context['company_name'] = profile.company_name
            
            apps = Application.objects.filter(job__company=profile)
            context['total_applications'] = apps.count()
            context['shortlisted_count'] = apps.filter(status='SHORTLISTED').count()
            context['pending_count'] = apps.filter(status='APPLIED').count()
            context['recent_applications'] = apps.select_related('student__user', 'job').order_by('-applied_at')[:5]
        return context

class CompanyJobListView(LoginRequiredMixin, CompanyRequiredMixin, ListView):
    model = Job
    template_name = 'placements/company_job_list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'company_profile'):
            return Job.objects.filter(company=self.request.user.company_profile).order_by('-created_at')
        return Job.objects.none()

class CompanyApplicationListView(LoginRequiredMixin, CompanyRequiredMixin, ListView):
    model = Application
    template_name = 'placements/company_application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'company_profile'):
            return Application.objects.filter(job__company=self.request.user.company_profile).select_related('student__user', 'job').prefetch_related('student__skills').order_by('-applied_at')
        return Application.objects.none()

class CompanyApplicationUpdateView(LoginRequiredMixin, CompanyRequiredMixin, UpdateView):
    model = Application
    form_class = CompanyApplicationUpdateForm
    template_name = 'placements/company_application_update.html'
    success_url = reverse_lazy('company_applications')
    
    def get_queryset(self):
        if hasattr(self.request.user, 'company_profile'):
            return super().get_queryset().filter(job__company=self.request.user.company_profile).select_related('student__user').prefetch_related('student__skills')
        return Application.objects.none()
    
    def form_valid(self, form):
        self.object = form.save()
        
        status = form.cleaned_data.get('status')
        scheduled_at = form.cleaned_data.get('interview_scheduled_at')
        mode = form.cleaned_data.get('interview_mode')
        meeting_link = form.cleaned_data.get('interview_meeting_link')
        venue = form.cleaned_data.get('interview_venue')
        notes = form.cleaned_data.get('interview_notes')
        
        if status == 'SHORTLISTED' and scheduled_at:
            interview, created = Interview.objects.get_or_create(
                application=self.object,
                defaults={'scheduled_at': scheduled_at}
            )
            interview.scheduled_at = scheduled_at
            interview.interview_mode = mode
            if mode == 'ONLINE':
                interview.meeting_link = meeting_link
            else:
                interview.meeting_link = venue
            interview.notes = notes
            interview.save()
            
            mode_display = "Online" if mode == 'ONLINE' else "In-Person"
            msg = f"{mode_display} Interview scheduled for {self.object.job.title} on {scheduled_at.strftime('%d %b, %Y - %I:%M %p')}."
            NotificationService.create_and_send(
                user=self.object.student.user,
                message=msg,
                email_subject="Interview Update",
                email_template="emails/interview_scheduled.html",
                context={
                    'student_name': self.object.student.user.first_name,
                    'job_title': self.object.job.title,
                    'company_name': self.object.job.company.company_name,
                    'scheduled_at': scheduled_at.strftime('%d %b, %Y - %I:%M %p'),
                    'mode': mode_display,
                    'link': meeting_link if mode == 'ONLINE' else venue,
                    'notes': notes,
                }
            )
            
            messages.success(self.request, "Interview details updated successfully and notification sent.")
            
        ApplicationService.update_application_status(
            self.object, 
            self.object.status, 
            remarks=self.object.remarks,
            updated_by_role='Employer'
        )
        
        messages.success(self.request, f"Application for {self.object.student.user.first_name} updated successfully.")
        return redirect(self.get_success_url())

from django.http import HttpResponse
from accounts.services.excel_import import BulkImportService

class BulkImportStudentsView(LoginRequiredMixin, TPORequiredMixin, TemplateView):
    template_name = 'placements/tpo_bulk_import.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Bulk Import Students'
        context['template_url'] = reverse('tpo_download_student_template')
        context['import_type'] = 'Students'
        return context
        
    def post(self, request, *args, **kwargs):
        if 'excel_file' not in request.FILES:
            messages.error(request, "Please upload an Excel file.")
            return redirect('tpo_bulk_import_students')
            
        file_obj = request.FILES['excel_file']
        if not file_obj.name.endswith('.xlsx'):
            messages.error(request, "Only .xlsx files are supported.")
            return redirect('tpo_bulk_import_students')
            
        try:
            results = BulkImportService.process_student_excel(file_obj)
            context = self.get_context_data()
            context['results'] = results
            return self.render_to_response(context)
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect('tpo_bulk_import_students')

class BulkImportCompaniesView(LoginRequiredMixin, TPORequiredMixin, TemplateView):
    template_name = 'placements/tpo_bulk_import.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Bulk Import Companies'
        context['template_url'] = reverse('tpo_download_company_template')
        context['import_type'] = 'Companies'
        return context
        
    def post(self, request, *args, **kwargs):
        if 'excel_file' not in request.FILES:
            messages.error(request, "Please upload an Excel file.")
            return redirect('tpo_bulk_import_companies')
            
        file_obj = request.FILES['excel_file']
        if not file_obj.name.endswith('.xlsx'):
            messages.error(request, "Only .xlsx files are supported.")
            return redirect('tpo_bulk_import_companies')
            
        try:
            results = BulkImportService.process_company_excel(file_obj)
            context = self.get_context_data()
            context['results'] = results
            return self.render_to_response(context)
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect('tpo_bulk_import_companies')

class DownloadStudentTemplateView(LoginRequiredMixin, TPORequiredMixin, View):
    def get(self, request):
        output = BulkImportService.generate_sample_student_excel()
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="student_import_template.xlsx"'
        return response

class DownloadCompanyTemplateView(LoginRequiredMixin, TPORequiredMixin, View):
    def get(self, request):
        output = BulkImportService.generate_sample_company_excel()
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="company_import_template.xlsx"'
        return response


from django.http import HttpResponse
def email_debug(request):
    from django.conf import settings
    try:
        from django.core.mail import send_mail
        send_mail('Test Render Email', 'Testing from Render server', settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], fail_silently=False)
        return HttpResponse('SEND SUCCESS')
    except Exception as e:
        import traceback
        return HttpResponse(f'ERROR: {str(e)} <br> {traceback.format_exc()}')

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from .forms import StudentSignUpForm
from .models import User

from django.contrib import messages
from core.services import NotificationService

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        admin_user = User.objects.filter(is_superuser=True).first()
        msg = "A new student has registered."
        login(self.request, user)
        messages.success(self.request, "Account created successfully! Welcome to the Campus Placement Platform.")
        
        # Notify student of successful signup
        NotificationService.create_and_send(
            user=admin_user,
            message=msg,
            email_subject="New Student Registration",
            email_template='emails/tpo_notification.html',
            context={
                'alert_title': 'New Student Registered',
                'alert_message': 'A new student has registered and is pending approval.',
                'details': {
                    'Name': f"{user.first_name} {user.last_name}",
                    'Email': user.email
                }
            }
        )
        
        return redirect('dashboard_redirect')

from .forms import CompanySignUpForm

class CompanySignUpView(CreateView):
    model = User
    form_class = CompanySignUpForm
    template_name = 'accounts/company_signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Recruiter profile created successfully! Welcome to the Campus Placement Platform.")
        
        # Notify company of successful signup
        NotificationService.create_and_send(
            user=user,
            message="Welcome to CampusConnect! Your recruiter profile has been created successfully.",
            email_subject="Welcome to CampusConnect",
            email_template="emails/base_notification.html",
            context={
                'title': 'Account Created',
                'message': 'Welcome to CampusConnect! Your recruiter profile has been created successfully.',
                'action_url': '#'
            }
        )

        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            NotificationService.create_and_send(
                user=admin_user,
                message="A new company has registered.",
                email_subject="New Company Registration",
                email_template='emails/tpo_notification.html',
                context={
                    'alert_title': 'New Company Registered',
                    'alert_message': 'A new company has registered on the platform.',
                    'details': {
                        'Company Name': form.cleaned_data.get('company_name'),
                        'HR Email': user.email
                    }
                }
            )
        
        return redirect('dashboard_redirect')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or 'User'}!")
        return super().form_valid(form)

class DashboardRedirectView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_admin or request.user.is_superuser:
            return redirect('tpo_dashboard')

        elif request.user.is_company:
            return redirect('company_dashboard')

        elif request.user.is_student:
            return redirect('student_dashboard')

        return redirect('login')

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully. See you again!")
    return redirect('login')

from django.http import HttpResponse

def init_tpo_admin(request):
    email = "tpo@college.edu"
    password = "SecureTPOPassword123!"
    
    # Auto-populate default branches
    from students.models import Branch, Skill
    
    branches = [
        {"name": "Computer Science and Engineering", "code": "CSE"},
        {"name": "Information Technology", "code": "IT"},
        {"name": "Electronics and Communication Engineering", "code": "ECE"},
        {"name": "Mechanical Engineering", "code": "ME"},
        {"name": "Civil Engineering", "code": "CE"},
        {"name": "Electrical Engineering", "code": "EE"}
    ]
    
    for b in branches:
        Branch.objects.get_or_create(name=b["name"], defaults={"code": b["code"]})
        
    # Auto-populate default skills
    skills = [
        "Python", "Java", "C++", "JavaScript", "Django", "React", "Angular", 
        "SQL", "Machine Learning", "Data Structures", "HTML5", "CSS3", "Node.js"
    ]
    
    for s in skills:
        Skill.objects.get_or_create(name=s)
    
    if User.objects.filter(email=email).exists():
        return HttpResponse("<h3>TPO Admin Account already exists!</h3><p>And default academic branches (CSE, IT, ECE, ME, CE) and technical skills have been successfully populated!</p><p>You can login using <strong>tpo@college.edu</strong></p>")
        
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name="Admin",
        last_name="TPO"
    )
    return HttpResponse(f"<h3>TPO Admin Account successfully initialized!</h3><p>Email: <strong>{email}</strong><br>Password: <strong>{password}</strong></p><p>Standard academic branches (CSE, IT, ECE, ME, CE, EE) and core engineering skills have been automatically seeded into the database!</p><p><a href='/login/'>Click here to Login</a></p>")

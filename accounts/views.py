from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from .forms import StudentSignUpForm
from .models import User

from django.contrib import messages

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Account created successfully! Welcome to the Campus Placement Platform.")
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
    
    if User.objects.filter(email=email).exists():
        return HttpResponse("<h3>TPO Admin Account already exists!</h3><p>You can login using <strong>tpo@college.edu</strong></p>")
        
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name="Admin",
        last_name="TPO"
    )
    return HttpResponse(f"<h3>TPO Admin Account successfully initialized!</h3><p>Email: <strong>{email}</strong><br>Password: <strong>{password}</strong></p><p><a href='/login/'>Click here to Login</a></p>")

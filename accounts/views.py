from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
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
        user = form.save(commit=False)
        user.is_active = False  # Enforce email verification
        user.save()
        
        # Profile creation handles itself via signals or forms
        form.save_m2m() if hasattr(form, 'save_m2m') else None
        
        # Generate token
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = self.request.build_absolute_uri(reverse_lazy('verify_email', kwargs={'uidb64': uidb64, 'token': token}))
        
        # Notify student to verify via EmailService
        from core.services import EmailService
        EmailService.send_welcome_email(user, verify_url, is_student=True, is_company=False)
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            NotificationService.create_and_send(
                user=admin_user,
                message="A new student has registered and is pending verification.",
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
        
        messages.success(self.request, "Account created successfully. Please check your email to verify your account before logging in.")
        return render(self.request, 'accounts/registration_pending.html', {'email': user.email})

from .forms import CompanySignUpForm

class CompanySignUpView(CreateView):
    model = User
    form_class = CompanySignUpForm
    template_name = 'accounts/company_signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Enforce email verification
        user.save()
        
        # Save related M2M data or related profile (CompanyProfile is handled in form.save usually or signals)
        if hasattr(form, 'save_m2m'):
            form.save_m2m()
        
        # Generate token
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = self.request.build_absolute_uri(reverse_lazy('verify_email', kwargs={'uidb64': uidb64, 'token': token}))
        
        # Notify company to verify
        from core.services import EmailService
        EmailService.send_welcome_email(user, verify_url, is_student=False, is_company=True)

        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            NotificationService.create_and_send(
                user=admin_user,
                message="A new company has registered and is pending verification.",
                email_subject="New Company Registration",
                email_template='emails/tpo_notification.html',
                context={
                    'alert_title': 'New Company Registered',
                    'alert_message': 'A new company has registered and needs email verification.',
                    'details': {
                        'Company Name': form.cleaned_data.get('company_name'),
                        'HR Email': user.email
                    }
                }
            )
        
        messages.success(self.request, "Account created successfully. Please check your email to verify your account before logging in.")
        return render(self.request, 'accounts/registration_pending.html', {'email': user.email})

from .forms import CustomAuthenticationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomAuthenticationForm

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
    email = "vg199r@gmail.com"
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
        return HttpResponse("<h3>TPO Admin Account already exists!</h3><p>And default academic branches (CSE, IT, ECE, ME, CE) and technical skills have been successfully populated!</p><p>You can login using <strong>vg199r@gmail.com</strong></p>")
        
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name="Admin",
        last_name="TPO"
    )
    return HttpResponse(f"<h3>TPO Admin Account successfully initialized!</h3><p>Email: <strong>{email}</strong><br>Password: <strong>{password}</strong></p><p>Standard academic branches (CSE, IT, ECE, ME, CE, EE) and core engineering skills have been automatically seeded into the database!</p><p><a href='/login/'>Click here to Login</a></p>")

def init_tpo(request):
    """
    Utility view to create initial TPO admin if none exists.
    Must be accessed manually (e.g., /accounts/init-tpo/).
    """
    if not User.objects.filter(is_admin=True).exists():
        admin = User.objects.create_superuser(
            email='vg199r@gmail.com',
            password='admin',
            first_name='TPO',
            last_name='Admin'
        )
        return render(request, 'accounts/init_tpo_success.html', {'admin': admin})
    return redirect('login')

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.cache import cache
from .models import AuditLog
from .forms import ForgotPasswordForm, SetNewPasswordForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class ForgotPasswordView(View):
    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, 'accounts/forgot_password.html', {'form': form})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            ip = get_client_ip(request)
            
            ip_key = f"forgot_pwd_ip_{ip}"
            email_key = f"forgot_pwd_email_{email}"
            
            ip_count = cache.get(ip_key, 0)
            email_count = cache.get(email_key, 0)
            
            if ip_count >= 20 or email_count >= 5:
                messages.error(request, "Too many requests. Please try again later.")
                return render(request, 'accounts/forgot_password.html', {'form': form})
                
            cache.set(ip_key, ip_count + 1, timeout=3600)
            cache.set(email_key, email_count + 1, timeout=3600)
            
            AuditLog.objects.create(email=email, action="Password reset requested", ip_address=ip)
            
            user = User.objects.filter(email=email).first()
            if user:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                
                reset_url = request.build_absolute_uri(reverse_lazy('reset_password', kwargs={'uidb64': uidb64, 'token': token}))
                
                from core.services import EmailService
                EmailService.send_password_reset(user, reset_url)
                
            messages.success(request, "If an account exists for this email, a password reset link has been sent.")
            return render(request, 'accounts/forgot_password.html', {'form': ForgotPasswordForm()})
            
        return render(request, 'accounts/forgot_password.html', {'form': form})

class ResetPasswordView(View):
    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        token_generator = PasswordResetTokenGenerator()
        
        if user is not None and token_generator.check_token(user, token):
            form = SetNewPasswordForm()
            return render(request, 'accounts/reset_password.html', {'form': form})
        else:
            AuditLog.objects.create(action="Invalid token access attempt", ip_address=get_client_ip(request))
            return render(request, 'accounts/reset_password_invalid.html')

    def post(self, request, uidb64, token):
        user = self.get_user(uidb64)
        token_generator = PasswordResetTokenGenerator()
        
        if user is not None and token_generator.check_token(user, token):
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.force_password_change = False
                user.save()
                AuditLog.objects.create(user=user, email=user.email, action="Password reset completed", ip_address=get_client_ip(request))
                return redirect('reset_password_success')
            return render(request, 'accounts/reset_password.html', {'form': form})
        else:
            AuditLog.objects.create(action="Invalid token access attempt (POST)", ip_address=get_client_ip(request))
            return render(request, 'accounts/reset_password_invalid.html')

class ResetPasswordSuccessView(View):
    def get(self, request):
        return render(request, 'accounts/reset_password_done.html')

class ForceChangePasswordView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.force_password_change:
            return redirect('dashboard_redirect')
        form = SetNewPasswordForm()
        return render(request, 'accounts/reset_password.html', {'form': form, 'force_change': True})

    def post(self, request):
        if not request.user.is_authenticated or not request.user.force_password_change:
            return redirect('dashboard_redirect')
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.force_password_change = False
            request.user.save()
            AuditLog.objects.create(user=request.user, email=request.user.email, action="Forced password change completed", ip_address=get_client_ip(request))
            login(request, request.user) # Re-authenticate
            messages.success(request, "Your password has been updated successfully.")
            return redirect('dashboard_redirect')
        return render(request, 'accounts/reset_password.html', {'form': form, 'force_change': True})

class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            AuditLog.objects.create(user=user, email=user.email, action="Email verified", ip_address=get_client_ip(request))
            messages.success(request, "Your email has been verified successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "The verification link is invalid or has expired.")
            return redirect('login')

class ResendVerificationEmailView(View):
    def post(self, request):
        email = request.POST.get('email')
        if email:
            user = User.objects.filter(email=email, is_active=False).first()
            if user:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                verify_url = request.build_absolute_uri(reverse_lazy('verify_email', kwargs={'uidb64': uidb64, 'token': token}))
                
                from core.services import EmailService
                EmailService.send_welcome_email(user, verify_url, is_student=user.is_student, is_company=user.is_company)
                
        messages.success(request, "If an inactive account exists for this email, a verification link has been sent.")
        return redirect('login')

class TPOProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/tpo_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('dashboard_redirect')
        return super().dispatch(request, *args, **kwargs)

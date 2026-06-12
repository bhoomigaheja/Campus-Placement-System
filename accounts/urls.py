from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.StudentSignUpView.as_view(), name='signup'),
    path('signup/company/', views.CompanySignUpView.as_view(), name='company_signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard_redirect'),
    path('init-tpo/', views.init_tpo_admin, name='init_tpo'),
    path('tpo/profile/', views.TPOProfileView.as_view(), name='tpo_profile'),
    
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password/success/', views.ResetPasswordSuccessView.as_view(), name='reset_password_success'),
    path('force-change-password/', views.ForceChangePasswordView.as_view(), name='force_change_password'),
    
    path('verify-email/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend_verification'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.StudentSignUpView.as_view(), name='signup'),
    path('signup/company/', views.CompanySignUpView.as_view(), name='company_signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard_redirect'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('profile/update/', views.StudentProfileUpdateView.as_view(), name='student_profile_update'),
]

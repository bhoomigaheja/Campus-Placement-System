from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import JobViewSet, ApplicationViewSet
from . import views

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'applications', ApplicationViewSet)

urlpatterns = [
    # APIs
    path('api/', include(router.urls)),
    
    # Old HTML Template Mappings
    path('dashboard/', views.TPODashboardView.as_view(), name='tpo_dashboard'),
    path('companies/', views.CompanyListView.as_view(), name='tpo_company_list'),
    path('companies/add/', views.CompanyCreateView.as_view(), name='tpo_company_form'),
    path('companies/delete/<int:pk>/', views.CompanyDeleteView.as_view(), name='tpo_company_delete'),
    path('drives/', views.DriveListView.as_view(), name='tpo_drive_list'),
    path('drives/add/', views.DriveCreateView.as_view(), name='tpo_drive_form'),
    path('drives/edit/<int:pk>/', views.DriveUpdateView.as_view(), name='tpo_drive_edit'),
    path('drives/delete/<int:pk>/', views.DriveDeleteView.as_view(), name='tpo_drive_delete'),
    path('drives/<int:pk>/', views.DriveDetailView.as_view(), name='tpo_drive_detail'),
    path('application/<int:pk>/status/', views.ApplicationStatusUpdateView.as_view(), name='tpo_application_update'),
    path('application/<int:app_pk>/interview/add/', views.InterviewScheduleCreateView.as_view(), name='tpo_interview_form'),
    
    # Bulk Imports
    path('students/import/', views.BulkImportStudentsView.as_view(), name='tpo_bulk_import_students'),
    path('students/import/template/', views.DownloadStudentTemplateView.as_view(), name='tpo_download_student_template'),
    path('companies/import/', views.BulkImportCompaniesView.as_view(), name='tpo_bulk_import_companies'),
    path('companies/import/template/', views.DownloadCompanyTemplateView.as_view(), name='tpo_download_company_template'),
    
    # Student Routes 
    path('student/drives/', views.StudentDriveListView.as_view(), name='student_drive_list'),
    path('student/drives/<int:pk>/', views.StudentDriveDetailView.as_view(), name='student_drive_detail'),
    path('student/drives/<int:pk>/apply/', views.ApplyDriveView.as_view(), name='student_drive_apply'),
    path('student/applications/', views.StudentApplicationsListView.as_view(), name='student_applications_list'),
    
    # Company Routes
    path('company/dashboard/', views.CompanyDashboardView.as_view(), name='company_dashboard'),
    path('company/jobs/', views.CompanyJobListView.as_view(), name='company_jobs'),
    path('company/applications/', views.CompanyApplicationListView.as_view(), name='company_applications'),
    path('company/application/<int:pk>/update/', views.CompanyApplicationUpdateView.as_view(), name='company_application_update'),
]

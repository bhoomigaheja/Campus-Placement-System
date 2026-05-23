from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from placements.models import Job, Application
from accounts.models import StudentProfile, CompanyProfile

class AnalyticsService:
    """
    Centralized service for generating statistics and trends.
    """
    
    @staticmethod
    def get_tpo_dashboard_stats():
        now = timezone.now()
        last_month = now - timedelta(days=30)
        two_months_ago = now - timedelta(days=60)
        
        # Current month counts
        total_students = StudentProfile.objects.count()
        total_companies = CompanyProfile.objects.count()
        total_drives = Job.objects.count()
        
        # Placements
        total_selected = Application.objects.filter(status='OFFERED').count()
        placement_percentage = round((total_selected / total_students * 100), 1) if total_students > 0 else 0
        
        # Trends (Current vs Previous Month)
        current_month_applications = Application.objects.filter(applied_at__gte=last_month).count()
        prev_month_applications = Application.objects.filter(applied_at__gte=two_months_ago, applied_at__lt=last_month).count()
        
        app_trend = 0
        if prev_month_applications > 0:
            app_trend = round(((current_month_applications - prev_month_applications) / prev_month_applications) * 100, 1)
        elif current_month_applications > 0:
            app_trend = 100
            
        current_month_drives = Job.objects.filter(created_at__gte=last_month).count()
        prev_month_drives = Job.objects.filter(created_at__gte=two_months_ago, created_at__lt=last_month).count()
        
        drive_trend = 0
        if prev_month_drives > 0:
            drive_trend = round(((current_month_drives - prev_month_drives) / prev_month_drives) * 100, 1)
        elif current_month_drives > 0:
            drive_trend = 100
            
        return {
            'total_students': total_students,
            'total_companies': total_companies,
            'total_drives': total_drives,
            'total_selected': total_selected,
            'placement_percentage': placement_percentage,
            'trends': {
                'applications': {
                    'value': current_month_applications,
                    'percentage': app_trend,
                    'is_positive': app_trend >= 0
                },
                'drives': {
                    'value': current_month_drives,
                    'percentage': drive_trend,
                    'is_positive': drive_trend >= 0
                }
            }
        }

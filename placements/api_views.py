from rest_framework import viewsets, permissions
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer
from .permissions import IsTPO, IsCompany

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related('company__user').prefetch_related('required_skills', 'eligible_branches').all()
    serializer_class = JobSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTPO | IsCompany]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('student__user', 'job__company').all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Application.objects.select_related('student__user', 'job__company').all()
        elif user.is_company:
            return Application.objects.filter(job__company=user.company_profile).select_related('student__user', 'job__company')
        elif user.is_student:
            return Application.objects.filter(student=user.student_profile).select_related('student__user', 'job__company')
        return Application.objects.none()

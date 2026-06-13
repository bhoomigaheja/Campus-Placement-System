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

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Job.objects.none()
        
        qs = Job.objects.select_related('company__user').prefetch_related('required_skills', 'eligible_branches')
        
        if user.is_admin or user.is_superuser:
            return qs.all()
        elif user.is_company:
            from django.db.models import Q
            return qs.filter(Q(status='APPROVED') | Q(company=user.company_profile))
        elif user.is_student:
            return qs.filter(status='APPROVED')
            
        return Job.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_company:
            serializer.save(company=user.company_profile, status='PENDING', created_by=user)
        else:
            status = self.request.data.get('status', 'APPROVED')
            serializer.save(created_by=user, status=status)

    def perform_update(self, serializer):
        user = self.request.user
        if user.is_company:
            serializer.save(status='PENDING')
        else:
            serializer.save()


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

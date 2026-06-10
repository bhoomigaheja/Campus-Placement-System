from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core import views_test as core_test_views
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='home'),
    path('', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('tpo/', include('placements.urls')),
    path('', include('core.urls')),
    path('test-email/', core_test_views.test_email_view, name='test_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

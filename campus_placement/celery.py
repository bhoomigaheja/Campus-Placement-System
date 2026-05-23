import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')

app = Celery('campus_placement')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

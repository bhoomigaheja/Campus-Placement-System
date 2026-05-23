import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from accounts.models import CompanyProfile
from django.db.models import Count

duplicates = CompanyProfile.objects.values('company_name').annotate(name_count=Count('company_name')).filter(name_count__gt=1)
count = 0
for dup in duplicates:
    name = dup['company_name']
    profiles = list(CompanyProfile.objects.filter(company_name=name).order_by('id'))
    # keep the first one
    for profile in profiles[1:]:
        print(f"Deleting duplicate company: {name} (ID: {profile.id})")
        profile.delete()
        count += 1
print(f"Duplicates resolved: {count} removed.")

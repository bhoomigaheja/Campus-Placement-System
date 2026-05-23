import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_placement.settings')
django.setup()

from placements.forms import PlacementDriveForm
from django.template import Template, Context

f = PlacementDriveForm()
t = Template('''
{% for checkbox in form.eligible_branches %}
    ITERATING... {{ checkbox.choice_label }}
{% empty %}
    EMPTY!
{% endfor %}
''')
c = Context({'form': f})
print(t.render(c))

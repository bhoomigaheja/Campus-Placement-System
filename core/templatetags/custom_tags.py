from django.template.defaulttags import register

@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key) if hasattr(dictionary, 'getlist') else dictionary.get(key, [])

from django.utils import timezone
from django.utils.timesince import timesince

@register.filter
def time_ago(value):
    if not value:
        return ""
    now = timezone.now()
    diff = now - value
    if diff.total_seconds() < 60:
        return "Just now"
    return f"{timesince(value)} ago"

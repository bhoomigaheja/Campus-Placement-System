from django import template
from core.utils.media_utils import MediaHelper

register = template.Library()

@register.filter
def file_exists(file_field):
    """
    Returns True if the file physically exists on storage.
    Usage: {% if profile.resume|file_exists %}
    """
    return MediaHelper.file_exists(file_field)

import os
from django.core.files.storage import default_storage

class MediaHelper:
    """
    Centralized utility for safe media file operations.
    """

    @staticmethod
    def file_exists(file_field):
        """
        Safely check if a FileField/ImageField has a physical file.
        """
        if not file_field or not file_field.name:
            return False
        return default_storage.exists(file_field.name)

    @staticmethod
    def safe_delete(file_field):
        """
        Safely delete the physical file associated with a FileField if it exists.
        Avoids crashes if the file was manually removed.
        """
        if not file_field or not file_field.name:
            return False
            
        try:
            if default_storage.exists(file_field.name):
                default_storage.delete(file_field.name)
                return True
        except Exception as e:
            # Log error in a real production system
            pass
        return False

    @staticmethod
    def get_safe_url(file_field, default_url=None):
        """
        Returns the file URL if it physically exists, otherwise returns a default URL or None.
        """
        if MediaHelper.file_exists(file_field):
            return file_field.url
        return default_url

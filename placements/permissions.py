from rest_framework import permissions

class IsTPO(permissions.BasePermission):
    """
    Allows access only to TPO users (is_admin or is_superuser).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser))

class IsCompany(permissions.BasePermission):
    """
    Allows access only to Company users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_company)

class IsStudent(permissions.BasePermission):
    """
    Allows access only to Student users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)

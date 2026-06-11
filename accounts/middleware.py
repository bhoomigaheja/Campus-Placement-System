from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.force_password_change:
            # Prevent infinite redirect loop
            allowed_paths = [
                reverse('reset_password_success'), # or any dedicated change password page
                reverse('logout'),
                # Note: They must use the forgot password flow if we don't build a custom change password page.
                # However, since they have their temporary password, a custom change password page is better.
                # Let's direct them to a new 'force_change_password' view.
                reverse('force_change_password'),
            ]
            if request.path not in allowed_paths and not request.path.startswith('/admin/'):
                messages.warning(request, "You must change your temporary password before accessing the platform.")
                return redirect('force_change_password')

        response = self.get_response(request)
        return response

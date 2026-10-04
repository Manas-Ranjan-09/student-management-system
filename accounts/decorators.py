from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You do not have administrative access to this page.")
    return _wrapped_view

def student_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_student:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You do not have student access to this page.")
    return _wrapped_view

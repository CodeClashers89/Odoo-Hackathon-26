from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from functools import wraps

def role_required(*allowed_roles):
    """
    Decorator for views that checks that the user has a specific role,
    raising PermissionDenied if not allowed.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # If not authenticated, login_required should handle this,
                # but just in case, we can redirect or raise. We'll rely on login_required.
                raise PermissionDenied
            
            user_role = getattr(request.user.profile, 'role', None)
            if user_role in allowed_roles or user_role == 'Admin':
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator

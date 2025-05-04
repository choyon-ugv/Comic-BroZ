from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('login')  # or any other page for normal users
        return view_func(request, *args, **kwargs)
    return _wrapped_view

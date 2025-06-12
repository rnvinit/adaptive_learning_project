# core_app/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Skip for API requests or admin URLs
            if request.path.startswith('/admin/') or request.path.startswith('/api/'):
                return response
                
            try:
                if request.user.userprofile.user_type == 'student' and not request.path.startswith('/student/'):
                    return redirect('student_dashboard')
                elif request.user.userprofile.user_type == 'educator' and not request.path.startswith('/educator/'):
                    return redirect('educator_dashboard')
            except AttributeError:
                pass
                
        return response
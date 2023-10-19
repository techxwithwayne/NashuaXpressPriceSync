from django.shortcuts import redirect
from django.urls import reverse

class CheckUserAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is not authenticated and the current URL is not the login page
        if not request.user.is_authenticated and not request.path == reverse('login'):
            return redirect('login')  # Redirect to the login page

        response = self.get_response(request)
        return response

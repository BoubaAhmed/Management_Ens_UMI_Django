from django.shortcuts import redirect
from django.urls import reverse

class RestrictAdminAccessMiddleware:
    """
    Middleware to restrict access to the admin panel for non-superusers,
    prevent superusers from accessing the custom dashboard,
    and ensure only users with at least one of the roles (is_encadrant or is_enseignant) can access the dashboard.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_url = reverse('admin:index')
        dashboard_url = reverse('dashboard')  # Replace 'dashboard' with the correct name for your dashboard view

        # Restrict access to the admin panel
        if request.path.startswith(admin_url):
            if request.user.is_authenticated and not request.user.is_superuser:
                return redirect(dashboard_url)
            
            if not (request.user.is_authenticated and request.user.is_superuser):
                return redirect('/')

        # Prevent superusers from accessing the custom dashboard
        if request.path.startswith(dashboard_url):
            if request.user.is_authenticated and request.user.is_superuser:
                return redirect(admin_url)  # Redirect superusers to the admin panel

            # Ensure only users with at least one of the roles (is_encadrant or is_enseignant) can access the dashboard
            if not (request.user.is_authenticated and (request.user.is_encadrant or request.user.is_enseignant)):
                return redirect('/')  # Redirect users who don't meet the criteria

        response = self.get_response(request)
        return response
 
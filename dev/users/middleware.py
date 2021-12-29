from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from django.urls import reverse
from django.contrib import auth

from .models import Online


class OnlineTrackerMiddleware(MiddlewareMixin):
    """Updates the OnlineUserActivity database whenever an authenticated user makes an HTTP request."""
    @staticmethod
    def process_request(request):
        user = request.user
        if not user.is_authenticated:
            return
        Online.update_or_create_online_status_for_user(user)
        # cache here for request.user online status


class RestrictViewsToAnonymousUsersMiddleware(MiddlewareMixin):
    """
    A middleware that restricts anonymous and non-superuser to admin panel.
    """
    def process_request(self, request):
        if request.path.startswith(reverse('admin:index')):
            if request.user.is_authenticated:
                if not (request.user.is_active and request.user.is_superuser):
                    raise Http404
            else:
                raise Http404

            
class ActiveUserMiddleware(MiddlewareMixin):
    """
    A middleware to logout in-active users.
    """

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        if not request.user.is_active:
            auth.logout(request)


class LastIPMiddleware(MiddlewareMixin):
    """
    A middleware to update request-user's last_ip
    """
    pass

        


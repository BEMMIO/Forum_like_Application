from django.conf import settings
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from functools import wraps

from ..users.models import User as user_cls
from django.shortcuts import redirect
from django.urls import reverse



def ajax_required(f):
    """A nice decorator to validate that a browser request is AJAX"""
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def is_authenticated_user(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not (user.is_authenticated and user.is_active):
            return redirect_to_login(next=request.get_full_path(),
                                     login_url=settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)

    return wrapper


def moderator_required(function=None,redirect_field_name=REDIRECT_FIELD_NAME,login_url=settings.LOGIN_URL):
	""" Decorator for views that checks that logged in user is a staff/admin.
	Redirects to login pag if neccessary.
	
	@moderator_required
	def view_func(request,***kwargs):
		pass
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_moderator and u.is_active,
		login_url = login_url,
		redirect_field_name=redirect_field_name
		)
	if function:
		return actual_decorator(function)
	return actual_decorator


def superuser_required(function=None,redirect_field_name=REDIRECT_FIELD_NAME,login_url=settings.LOGIN_URL):
	""" Decorator for views that checks that logged in user is a superuser/admin.
	Redirects to login pag if neccessary.
	
	@superuser_required
	def view_func(request,***kwargs):
		pass
	"""
	actual_decorator = user_passes_test(
		lambda u: u.is_active and u.is_superuser,
		login_url = login_url,
		redirect_field_name=redirect_field_name
		)
	if function:
		return actual_decorator(function)
	return actual_decorator


def owner_required(f):
    def wrap(request, *args, **kwargs):
        user = user_cls._default_manager.get(username=kwargs['username'])
        if request.user == user:
            return f(request, *args, **kwargs)
        else:
            raise PermissionDenied('You don\'t have permission to perform action.')

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def anonymous_required(f):
	""" Decorator to prevent already login-authenticated users from access this view"""
	def wrap(request,*args,**kwargs):
		if request.user.is_authenticated and request.user.is_active:
			return redirect(settings.LOGIN_REDIRECT_URL)
		else:
			return f(request,*args,**kwargs)

	wrap.__doc__ = f.__doc__
	wrap.__name__ = f.__name__
	return wrap

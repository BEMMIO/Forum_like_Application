import logging

from django.contrib import auth
from django.urls import reverse
from django.conf import settings
from django.contrib import messages

from django.shortcuts import (
    get_object_or_404,
    render,
    redirect
) 
from django.contrib.auth import (
    authenticate,
    get_backends,
    login as django_login,
    logout as django_logout,
)

from django.utils.http import is_safe_url
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from django.http import (
	HttpResponse,
	Http404,
	HttpResponseRedirect,
	HttpResponseForbidden
)
from django.views.decorators.debug import sensitive_post_parameters

from dev.invitation.models import Invitation
from dev.users.services import User as user_cls
from dev.core.decorators import anonymous_required
from ..forms import (
	AuthenticationForm,
	RegisterationForm
)

from ..services import get_user_for_hashed_email_and_code

backend_auth = getattr(settings,"BACKEND_AUTH")

logger = logging.getLogger(__name__)


@never_cache
@csrf_protect
@login_required
def logout(request):
	auth.logout(request)
	return redirect(settings.LOGOUT_REDIRECT_URL)

	
# rate-limit : ip by 5/min
@anonymous_required
def register(request,**kwargs):
	# ToDo : Template error-messages not displaying.
	from ..services import get_user_for_hashed_email_and_code

	user = get_user_for_hashed_email_and_code(hashed_email=kwargs.get('hash_email'),code=kwargs.get('code'))
	
	if user is None:
		raise HttpResponseForbidden()

	invitation = Invitation.get_invitation_for_code_or_raise_404(user)

	is_expired = False

	if not invitation.is_expired() and not user.is_active:
		if request.method == "POST":
			form = RegisterationForm(invitation=invitation,data=request.POST)
			if form.is_valid():
				print("valid")
				_user = form.save()
				auth.login(request,_user,backend=backend_auth)

				request.session["is_new_user"] = True

				return redirect(settings.LOGIN_REDIRECT_URL)
			else:
				print("in-valid credential")
	else:
		template_name = 'accounts/auth/user_registered_already.html'
		return TemplateResponse(request,template_name,{})

	template_name = 'accounts/auth/accounts_register.html'

	form = RegisterationForm(invitation=invitation)

	template_data = {
	"form":form,
	"is_expired":is_expired,
	}
	return TemplateResponse(request,template_name,template_data)

from ratelimit.decorators import ratelimit


# rate-limit
@anonymous_required
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
	# ToDo : use Misago authentication guide.
	# Fix : redirect-to url,_next
	# error messages not displaying
	# use google recapture api
	
	from dev.core.utils import get_next

	login_fm = AuthenticationForm()

	_next = ""

	if request.method == "POST":
		_next = get_next(request)
		print("next url : ",_next)

		login_fm = AuthenticationForm(data=request.POST)

		if login_fm.is_valid():
			cd = login_fm.cleaned_data
			username = cd["username"]
			password = cd["password"]
			remember_me = cd["remember_me"]

			user = auth.authenticate(username=username,password=password)
			if not user is None and user.is_active:

				auth.login(request,user,backend=backend_auth)

				A_MONTH = 30 * 24 * 60 * 60 # session stored for 1 month.

				if remember_me in request.POST:
					request.session.set_expiry(A_MONTH)
				else:
					request.session.set_expiry(0)

				if not _next or _next is None:
					return redirect(settings.LOGIN_REDIRECT_URL)
				return _next
			else:
				print("in-valid credentials")
		else:
			print("in-valid credentials")

	template_name = 'accounts/auth/accounts_login.html'
	template_data = {
	'login_fm':login_fm,
	}
	return TemplateResponse(request,template_name,template_data)

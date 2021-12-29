from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse,Http404,JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from dev.users.services import User


# Create your views here.
@login_required
def user_profile(request,username,template_name="accounts/user/user.html"):
	"""
	View : user_profile

	Response data :

	[*] user articles

	[*] user questions/answers

	[*] commented articles as done in Hashnode.com

	[*] followers & following

	[*] buttons - follow/unfollow (not owner)

	+ Link to Settings
			
	"""

	try:
		user = User._default_manager.get(username__iexact=username)
	except User.DoesNotExist:
		raise Http404

	# user data.



	template_data = {
	"user" : user,
	}
	return TemplateResponse(request,template_name,template_data)
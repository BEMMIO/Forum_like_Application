from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect
) 

from dev.invitation.forms import InvitationForm
from dev.invitation.models import Invitation


@login_required
def create_invitation(request,**kwargs):

	form = InvitationForm(request)

	qs = Invitation.objects.select_related("invite_to_user") 

	qs = qs.filter(invite_from_user=request.user)

	if request.method == "POST":
		form = InvitationForm(request,data=request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Invitation email is sent to {}'.format(request.POST["invite_to_user_email"]))
			return redirect("accounts:create-invitation")
		else:
			pass

	template_name = 'invitation/invitation_create.html'
	template_data = {
	"form":form,
	"active_invites_users":qs,
	}
	return TemplateResponse(request,template_name,template_data)
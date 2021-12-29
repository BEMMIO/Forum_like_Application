import logging

from datetime import timedelta
from config.celery import app
from django.conf import settings
from django.template.loader import render_to_string 
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.core.mail import BadHeaderError

from dev.core.emails import send_registered_email_to_invited_user
from dev.accounts.services import create_inactive_user_account_from_email as create_user


logger = logging.getLogger(__name__)



@app.task
# celery perform computational tasks
def test_celery_func():
	for i in range(80):
		print(i)
	return " Celery is Working !"


@app.task
def create_new_user_task(invitation_obj):
	user = create_user(user_email=invitation_obj.invite_to_user_email,
	invite_code=invitation_obj.invite_token)
	invitation_obj.invite_to_user = user
	invitation_obj.save(update_fields=["invite_to_user"])


@app.task
def send_invite_email(invitation_obj):
	send_registered_email_to_invited_user(
			to_email=invitation_obj.invite_to_user_email,
			message=invitation_obj.message,
			code=invitation_obj.invite_token,
			hash_email=invitation_obj.invite_to_user.email_hashed)


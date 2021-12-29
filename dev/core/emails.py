from django.conf import settings
import logging

from django.template.loader import render_to_string 
from django.template.loader import get_template
from django.core.mail import BadHeaderError
from django.core.mail import EmailMessage

from .utils import get_current_site_for_this_project


logger = logging.getLogger(__name__)


REGISTER_EMAIL_TEMPLATE = "accounts/emails/registeration_email.html"


def send_registered_email_to_invited_user(*,to_email:str,message:str = '',code:str,hash_email:str,request=None) -> None:

	template_subject = "Invitation"
	template_message = message
	email_from = settings.DEFAULT_FROM_EMAIL
	email_to = [to_email]
	template_mail = REGISTER_EMAIL_TEMPLATE

	# site setup
	site = get_current_site_for_this_project()

	if request is None:
		protocol = "http"
	else:
		protocol = 'https' if request.is_secure() else 'http'

	user_email_hash = hash_email.rstrip()

	code = code

	url_ = "{protocol}://{site}/a/register/{user_email_hash}/{code}"

	url = url_.format(protocol=protocol,site=site,user_email_hash=user_email_hash,code=code)

	invitation_verification_url = "/invitation/verification-link/"

	# {protocol}://{site}/accounts/register/{user_email_hash}/{code} # ToDo ; change user_email_hash to user uuid

	# eg. http://127.0.0.1:8000/a/register/wgedg6hghg$56dhdgh787==hd/CD09-TG4P-YURW

	template_data = {
	"domain":site,
	"message":template_message,
	"code":code,
	"url":url,
	"invite_paste_code_url":invitation_verification_url,
	}

	message_body = get_template(
		template_mail
	).render(template_data)

	email_ = EmailMessage(
		template_subject,message_body,email_from,email_to
	)
	email_.content_subtype = "html"

	try:
		email_.send()
	except BadHeaderError as e:
		logger.error(e)
	logger.debug("mail sent to {email_to}".format(email_to=email_to))
from django.core.exceptions import ValidationError

User = apps.get_model('users', 'User') 

Invitation = apps.get_model('invitation','Invitation')


def validate(email):
	# runs : validate_is_required_email,validate_email_unique,validate_invite_to_email
	pass


def validate_is_valid_email(email):
	data = data.split("@")[:-1]
	dots = "".join(data).count(".")
	if dots >= 2:
		raise ValidationError("This email type is not accepted.")
	return True


# Message
def validate_message_content(text):
	pass
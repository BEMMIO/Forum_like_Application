import re

from django.core.validators import validate_email as validate_email_content
from django.core.exceptions import ValidationError
from django.apps import apps


USERNAME_RE = re.compile(r"^[0-9a-z]+$", re.IGNORECASE)

User = apps.get_model('users', 'User') 




def check_full_name(data = None):

	if data is None:
		return False

	data_ = data.split()

	if len(data_) == 2 :
		if (len(data_[0]) or len(data_[1])) < 4:
			return False
		return True

	return False
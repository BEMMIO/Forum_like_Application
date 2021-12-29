import logging
import uuid
import re
import os
import pytz
import pickle
import base64

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.core import validators
from django.utils import timezone
from django.apps import apps
from django.db import models


from .online import Online


logger = logging.getLogger(__name__)


base64_encode = base64.encodebytes if hasattr(base64,'encodebytes') else base64.encodestring
base64_decode = base64.decodebytes if hasattr(base64,'decodebytes') else base64.decodestring


def email_to_db(email):
	# hash-user-email
	return base64_encode(pickle.dumps(email)).decode('ascii')



def db_to_email(data):
	if data == "":
		return
	else:
		try:
			data = data.encode('ascii')
		except AttributeError:
			pass
		try:
			return pickle.loads(base64_decode(data))
		except (TypeError,pickle.UnpicklingError,base64.binascii.Error,AttributeError):
			try:
				return pickle.loads(data)
			except (TypeError,pickle.UnpicklingError,AttributeError):
				return



class UserManager(BaseUserManager):
	def create_user(self,username,email,password=None,is_active=True,is_staff=False,**kwargs):
		"""create a user instance given email and password"""
		email = UserManager.normalize_email(email)

		user = self.model(
			username=username,email=email,is_active=is_active,is_staff=is_staff,**kwargs
		)

		if not username:
			raise ValueError("User must have an username.")

		if not email:
			raise ValueError("User must have an email address.")

		if password:
			user.set_password(password)
		user.save()
		
		# Online tracker
		Online.update_or_create_online_status_for_user(user)

		return user

	def create_superuser(self, username,email, password=None, **kwargs):
		return self.create_user(username,email,password,is_staff=True,is_superuser=True,**kwargs)


def get_default_uuid():
    return str(uuid.uuid4().hex)


def avatar_upload_dir(user_obj,filename):
	filename,ext = os.path.splitext(filename)
	return os.path.join(
		'avatar_images',
		'avatar_{uuid}_{filename}{ext}'.format(
			uuid=user_obj.uuid,filename=filename,ext=ext))




class User(PermissionsMixin,AbstractBaseUser):
	uuid 				=		models.CharField(max_length=32,editable=False,null=False,
								blank=False,unique=True,default=get_default_uuid)

	username 			=		models.CharField(max_length=255,unique=True,
								help_text=("Required. 30 characters or fewer. letters, numbers, and "
								"/./-/_ characters."),
								validators=[validators.RegexValidator(re.compile(r"^[\w.-]+$"),("Enter a valid username."), "invalid")])

	email 				=		models.EmailField(verbose_name = ("e-mail address"), max_length=255, null=False, blank=False, unique=True)

	email_hashed 		=		models.CharField(verbose_name = ("e-mail hashed"), max_length=425, null=True, blank=True)

	is_active   		=  		models.BooleanField(verbose_name = ("active"),default=True,help_text = ("Designates whether this user should be treated as "
								"active. Unselect this instead of deleting accounts."))

	is_staff    		=       models.BooleanField(verbose_name = ('staff status'), default=False,
								help_text="Designates whether the user can log into this admin site.")

	full_name 			=		models.CharField(verbose_name = ("Full name"), max_length=256, blank=True)

	is_moderator 		=		models.BooleanField(blank=True,null=True,default=False,help_text=("Designates whether the user has"
								" moderators privileges."))

	is_online_presence_hidden 	= models.BooleanField(verbose_name=("Is Online presence hidden?"),default=False)

	date_joined 		= 		models.DateTimeField(verbose_name = ("date joined"),blank=True,null=True,
								help_text="Designates the date user accepted invitation token")

	invite_code 		=		models.CharField(verbose_name = ("Invite Code"), max_length=16, blank=True,null=True)

	joined_from_ip 		=		models.GenericIPAddressField(null=True, blank=True)

	avatar_tmp 			= 		models.ImageField(verbose_name = ("user default avatar"),max_length=255,blank=True,null=True)

	avatar_src 		 	= 		models.ImageField(upload_to=avatar_upload_dir,verbose_name = ("user uploaded avatar "),max_length=255,blank=True,null=True)

	created_date		=		models.DateTimeField(auto_now_add=True,blank=True,null=True)

	modified_date 		=		models.DateTimeField(auto_now=True,blank=True,null=True)


	USERNAME_FIELD 		= 		"username"
	REQUIRED_FIELDS 	= 		["email"]


	objects 			=	UserManager()


	class Meta:
		verbose_name 	= "user"
		verbose_name_plural = "users"
		ordering 	= ["username"]


	def __str__(self):
		if self.full_name:
			return f"{self.full_name}"
		return f"{self.username}"


	def save(self,*args,**kwargs):
		if not self.id:# self is new
			self._set_email(self.email)
			if self.is_superuser:
				self.is_moderator = True
		super(self.__class__,self).save(*args,**kwargs)


	def clean(self):
		super().clean()
		self.username = self.normalize_username(self.username)
		self.email 	  = self.__class__.normalize_email(self.email)	


	def _set_email(self,data): #new
		self.email_hashed = email_to_db(data)


	def _get_email(self): #new
		return db_to_email(self.email_hashed)


	def get_email(self): #new
		return self._get_email()

	@property
	def get_user_avatar(self):
		# cache me!
		if not self.avatar_src or self.avatar_src is None:
			return self.avatar_tmp.url
		return self.avatar_src.url

	def get_full_name(self):
		if self.full_name and not self.full_name is None:
			return self.full_name
		return self.username


	def get_short_name(self):

		if self.full_name and not self.full_name == "":
			return self.full_name.split()[0]
		return ""


	@property
	def better_joined_datetime(self):
		from ...core.utils.time import better_readable_datetime

		return better_readable_datetime(self.date_joined)


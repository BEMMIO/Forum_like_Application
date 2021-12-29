import uuid

from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings
from django.db import models as m


__all__ = ['Invitation','InvitationChoices']

# Create your models here.
def get_default_uuid():
    return str(uuid.uuid4().hex)


class InvitationChoices:
	SENT  	 = 1
	ACCEPTED = 2
	EXPIRED  = 3

	CHOICES = [
		(SENT,'Sent'),
		(ACCEPTED,'Accepted'),
		(EXPIRED,'Expired'),
	]



class Invitation(m.Model):

	uuid 						=		m.CharField(max_length=32,editable=False,null=False,
								blank=False,unique=True,default=get_default_uuid)

	invite_from_user 			=		m.ForeignKey(to=settings.AUTH_USER_MODEL,blank=True,null=True,
								verbose_name=("invitation from user"),related_name="invites_from_user",
								on_delete=m.CASCADE)

	invite_to_user_email		=		m.EmailField(max_length=255,verbose_name="Email",unique=True,blank=False,null=False)


	invite_to_user 				=		m.OneToOneField(to=settings.AUTH_USER_MODEL,blank=True,null=True,
								on_delete=m.CASCADE,related_name="invite")


	invite_token 				=		m.CharField(max_length=15,blank=True,null=True,editable = True,
								verbose_name=("Token"))

	message 					=		m.TextField(max_length=225,blank=True,null=True,
								verbose_name=("Message"))

	status 						= 		m.PositiveIntegerField(blank=True,null=True,
								choices=InvitationChoices.CHOICES,verbose_name="Invite Status")

	sent_date 					=		m.DateTimeField(verbose_name="Sent Date",blank=True,null=True)


	created_date				=		m.DateTimeField(auto_now_add=True)


	class Meta:
		ordering = (("-created_date"),)
		verbose_name    = "Invitation"
		verbose_name_plural = "Invitation's"
		unique_together = (("invite_from_user", "invite_to_user_email","invite_token"),)


	def __str__(self):
		return "{0} sent an invite to {1}".format(self.invite_from_user.username,self.invite_to_user_email)


	def save(self,*args,**kwargs):
		
		self.invite_to_user_email = self.invite_to_user_email.lower()

		from .services import generate_random_code_for_invite
		if not self.id:
			self.invite_token = generate_random_code_for_invite()
		try:
			super(Invitation,self).save(*args,**kwargs)
		except IntegrityError:
			pass


	def clean(self):
		pass


	def invite_sent(self):
		self.status = InvitationChoices.SENT


	def invite_accepted(self):
		self.status = InvitationChoices.ACCEPTED
		self.save(update_fields=["status"])


	def is_expired(self):

		expiration_days = 21 # sent_date + 21 days - to expiry
		expiration_date = self.sent_date + timezone.timedelta(days=expiration_days)
		if timezone.now() >= expiration_date:
			return True
		return False


	@classmethod
	def get_invitation_for_code_or_raise_404(cls,user):

		try:
			return cls._default_manager.filter(invite_token__iexact=user.invite_code).\
			select_related("invite_to_user","invite_from_user").get()
		except (cls.DoesNotExist,IndexError):
			raise Http404


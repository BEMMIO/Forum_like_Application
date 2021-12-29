from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import Http404
from django.apps import apps
from django.db import models as m

from .users import User



class Follow(m.Model):
	''' Follow Model for DevBlog User '''
	to_user					= m.ForeignKey(to=settings.AUTH_USER_MODEL,on_delete=m.CASCADE,related_name='followers')
	from_user				= m.ForeignKey(to=settings.AUTH_USER_MODEL,on_delete=m.CASCADE,related_name='followings')

	created					= m.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together 	= (('to_user','from_user'),)
		ordering 			= ('-created',)


	def save(self,*args,**kwargs):
		is_self = self.to_user == self.from_user
		if is_self:
			raise ValueError('You can\'t follow yourself')
		return super(Follow,self).save(*args,**kwargs)


	def __str__(self):
		return "{0} is following {1}".format(self.from_user.username,self.to_user.username)


	@classmethod
	def get_people_user_follows(cls,user):
		# cache me!
		user_followings = cls.objects.filter(from_user=user).values_list('to_user',flat=True)
		return User._default_manager.filter(id__in=user_followings)
		

	@classmethod
	def get_people_following_user(cls,user):
		# cache me!
		user_followers = cls.objects.filter(to_user=user).values_list('from_user',flat=True)
		return User._default_manager.filter(id__in=user_followers)


	@classmethod
	def get_mutual_followers(cls,user):
		# cache me!
		follows = cls.objects.filter(from_user=user).values_list('to_user',
			flat=True)
		following = cls.objects.filter(to_user=user).values_list('from_user',
			flat=True)
		return User._default_manager.filter(
			id__in=set(follow).intersection(set(following)))


	@classmethod
	def from_user__to_user_switch(cls,from_user:User,to_user:User) -> None:
		pass

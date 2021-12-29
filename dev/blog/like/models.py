from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings
from django.db import models



class Like(models.Model):
	content_type 	= models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
	object_id 		= models.PositiveIntegerField()
	content_object 	= GenericForeignKey("content_type", "object_id")
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL,
										null=False,
										blank=False,
										related_name="likes",
										on_delete=models.CASCADE)


	created_date	= models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Like"
		verbose_name_plural = "Likes"
		index_together = ("content_type", "object_id")
		unique_together 	= ("content_type", "object_id", "user")


	def save(self,*args,**kwargs):
		try:
			super(Like,self).save(*args,**kwargs)
		except IntegrityError: # first come is first serve in Like
			pass


	def __str__(self):
		return "{0} has liked.".format(self.user.username)

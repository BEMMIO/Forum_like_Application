from django.utils import timezone
from django.db import models as m
from django.db import IntegrityError
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(m.Model):

    commented_by	 = m.ForeignKey(settings.AUTH_USER_MODEL, 
    								null=False, 
    								blank=False,
    								related_name="comments", 
    								on_delete=m.CASCADE)

    content_type	 = m.ForeignKey("contenttypes.ContentType", on_delete=m.CASCADE)

    object_id 		 = m.IntegerField()

    content_object   = GenericForeignKey("content_type", "object_id")

    content 		 = m.TextField(blank=False,null=False,max_length=350)

    created_date 	 = m.DateTimeField(default=timezone.now)

    ip 				 = m.GenericIPAddressField(null=True,blank=True)

    


    class Meta:
    	verbose_name = "Comment"
    	verbose_name_plural = "Comments"
    	index_together = ("content_type", "object_id")
    	unique_together = ("content_type", "object_id", "commented_by")

    def __str__(self):
        return "pk=%d" % self.pk  # pragma: no cover

    def save(self,*args,**kwargs):
    	try:
    		super().save(*args,**kwargs)
    	except IntegrityError:
    		pass
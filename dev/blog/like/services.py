from django.db.transaction import atomic
from django.apps import apps
from django.contrib.auth import get_user_model

from .models import Like as model_cls
from ..signals import article_is_reacted_to as is_reacted_to

# article model

def switch_like(obj, user):
    """Add a like to an object.
    If the user has already liked the object unlike user, else user like object.
    :param obj: Any Django model instance.
    :param user: User adding the like. :class:`~dev.users.models.User` instance.
    """
    obj_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(obj)
    with atomic():
        like, is_liked = model_cls.objects.get_or_create(content_type=obj_type, object_id=obj.id, user=user)
        # signal : article is reacted-to : liked/unliked
        is_reacted_to.send(sender=None,article=obj,is_liked=is_liked)
        if not is_liked:
        	like.delete()
    return is_liked
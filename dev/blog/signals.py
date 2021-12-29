from django.dispatch import Signal
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save,pre_delete

from ..core.utils.slug_generator import unique_slug_generator
from .color_codes import generate_random_predefined_hex_color
from .models import Board,Article
from .choices import ArticleStatus


# Defined Signals
article_is_deleted = Signal(providing_args=["article"])
article_is_viewed = Signal(providing_args=["article","request"]) # used
article_is_reacted_to = Signal(providing_args=["article","is_liked"]) # used

drafted_article_is_created = Signal(providing_args=["article","board"])
drafted_article_is_deleted = Signal(providing_args=["article","board"])
drafted_article_is_edited = Signal(providing_args=["article","board"])

published_article_is_created = Signal(providing_args=["article","board"])
article_is_edited = Signal(providing_args=["article"])

# Signal comments
comment_is_added = Signal(providing_args=["article"])
comment_is_deleted = Signal(providing_args=["article"])


@receiver(pre_save,sender=Board)
def board_pre_save_reciever(sender,instance,*args,**kwargs):
	if not instance.slug:
		instance.slug = unique_slug_generator(instance)
	if not instance.color:
		instance.color = generate_random_predefined_hex_color()


@receiver(pre_save,sender=Article)
def article_pre_save_reciever(sender,instance,*args,**kwargs):
	if not instance.slug:
		instance.slug = unique_slug_generator(instance)


@receiver(pre_delete,sender=Article)
def article_deleted_receiver(sender,instance,*args,**kwargs):
	if instance.image.storage.exists(instance.image.name):
		instance.image.delete(save=False)


@receiver(article_is_viewed)
def article_is_viewed_reciever(sender,**kwargs):
	"""
	Signal to be fired on when an article `published article`
	is viewed.
	"""
	article = kwargs["article"]
	if article.status == ArticleStatus.P:
		session_key = "viewed_{}".format(article.id)
		if not kwargs["request"].session.get(session_key,False):
			article.incr_views
			kwargs["request"].session[session_key] = True
	else:
		pass


@receiver(article_is_reacted_to)
def article_is_reacted_to_reciever(sender,**kwargs):
	# Signal-Reciever to handle Like/UnLike Counter.
	if kwargs['is_liked']:
		kwargs['article'].incr_like
	else:
		kwargs['article'].decr_like


@receiver(comment_is_added)
def article_comment_reciever_function(sender,**kwargs):
	# Signal-Receiver to handle Comments : in-crement
	kwargs['article'].incr_comment


@receiver(comment_is_deleted)
def article_comment_reciever_function(sender,**kwargs):
	# Signal-Receiver to handle Comments : de-crement
	kwargs['article'].decr_comment


@receiver(article_is_edited)
def article_is_edited_reciever_function(sender,**kwargs):
	# Edit - remove old article image if any from storage location.
	pass
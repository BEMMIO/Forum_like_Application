import os
import pytz
import logging
import readtime
import datetime

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.utils.functional import cached_property
from django.db.models import JSONField
from django.db import transaction as tx
from django.utils.text import Truncator
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from django.db import models as m
from django.conf import settings
from django.urls import reverse
from django.db.models import F
from django.db.models import Q
from django.apps import apps

# Third Party
from taggit.managers import TaggableManager

# Project imports
from ..core.conf import Dev
from ..users.models import User as user_cls
from .choices import ArticleStatus


logger = logging.getLogger(__name__)




# board QuerySet
class BoardQuerySet(m.query.QuerySet):

	def boards_ranking_by_viewed_counts(self):
		# return a qs of all published articles in this board in order of views
		return self.order_by("-board_view_counts")


	def boards_rank_by_articles_counts(self):
		# rank hits by articles counts & comments count.
		return self.order_by("-articles_count")


	def get_a_board_article_qs(self,pk):
		# get a boards article.
		qs = self.get(id=pk).articles.filter(status="p")

		# get only published articles for `this` board with `pk`
		return qs.select_related("created_by","board")




# Board model.

class Board(m.Model):

	created_by  =   m.ForeignKey(to=user_cls,
								verbose_name="created user",
								related_name='boards',
								blank=True,
								null=False,
								on_delete=m.CASCADE)

	title 		=   m.CharField(max_length=55,
						  verbose_name="title",
						  blank=True,
						  null=True)

	description = 	m.TextField(max_length=200,
						  verbose_name="description",
						  blank=True,
						  null=True)

	slug 		=  	m.SlugField(max_length=120,verbose_name="title slug",
									allow_unicode=True,unique=True,blank=True,null=True)

	color 		=	m.CharField(max_length=7,
						  verbose_name="board color",
						  blank=True,
						  null=True)

	last_article = m.ForeignKey(to="blog.Article",blank=True,null=True,on_delete=m.SET_NULL,related_name="+")

	created_date   = m.DateTimeField(auto_now_add=True)

	modified_date  = m.DateTimeField(auto_now=True)


	# de-normalize field data.
	# stats: `most active board` 
	articles_count = m.PositiveIntegerField(blank=True,null=True,verbose_name="articles count",default=0)

	joined_users_count = m.PositiveIntegerField(blank=True,null=True,verbose_name="joined users",default=0)

	# stats:  `most viewed board`
	board_view_counts = m.PositiveIntegerField(blank=True,null=True,verbose_name="board view count",default=0)

	objects 	= BoardQuerySet.as_manager()


	class Meta:
		ordering  = (("-created_date"),)
		verbose_name = "Board"
		verbose_name_plural = "Board's"


	def __str__(self):
		return self.title


	def save(self,*args,**kwargs):
		# signals.board_is_created.send(sender=self)
		super(self.__class__,self).save(*args,**kwargs)


	def update_articles_count(self):
		"""
		This method updates board's article count for every
		created/deleted on an article.
		"""
		self.articles_count = self.articles.filter(status=ArticleStatus.P).count()
		self.save(update_fields=["articles_count"])
	update_articles_count.alters_data = True


	def incr_views(self):
		# board views count - board is viewed
		pass


	def update_views_count(self):
		# views count of all board article view-counts
		# ToDo : include board views count .
		view_count = 0
		for article in self.articles.all():
			view_count += article.views_counts
		self.board_view_counts = view_count
		self.save(update_fields=["board_view_counts"])


	def update_last_article(self):
		# update last article for this board - created & delete on article
		qs = self.articles.filter(status=ArticleStatus.P).order_by("-published_date")
		if qs.exists():
			self.last_article = qs[0]
		else:
			self.last_article = None
		self.save(update_fields=["last_article"])
		# update board article counts for any changes in `thi`s board
		self.update_articles_count()
	update_last_article.alters_data = True





class ArticleQuerySet(m.query.QuerySet):

	def get_published_articles(self):
		# NOTE : cache me!
		# queryset of published articles
		conditions = \
			(
				Q(
				status=ArticleStatus.P
				) & Q(
				published_date__isnull=False
				) 

				  & Q(
				published_date__lte=timezone.now()
				)
				& Q(
				is_deleted__isnull=True
				)
			)
		return self.filter(conditions)


	def get_currently_published_articles(self,sort_by=None):
		# cache me!
		# return queryset of currently published articles `Last-Come-Last-Show`
		sort_by = sort_by or '-published_date'
		return self.get_published_articles().order_by(sort_by)


	def get_most_viewed_articles(self):
		# cache me!
		# return queryset of popular/trending/most-viewed published articles `Last-Come-Last-Show`
		return self.get_published_articles().order_by('-views_counts')


	def get_drafted_articles(self):
		# cache me!
		# queryset of drafted articles
		conditions = \
		(
			Q(
			  published_date__isnull=True
			) &

			Q(
				is_deleted__isnull = True
			)
			&

			Q(
			  status=ArticleStatus.D
			)
		)
		return self.filter(conditions)

	def user_drafted_articles(self,user):
		# qs of all drafted articles in all boards for user
		# cache me
		return self.get_drafted_articles().filter(created_by=user)

	def user_drafted_articles_in_this_board(self,user,board):
		# cache me!
		# return qs of drafted articles for user in given board
		return self.user_drafted_articles(user).filter(board__title__iexact=board.title)


def article_cover_upload_dir(article_obj,filename):
	# upload function.
	filename,ext = os.path.splitext(filename)
	return os.path.join(
		'article_cover_images',
		'cover_image_{slug}_{filename}{ext}'.format(
			slug=article_obj.slug,filename=filename.lower(),ext=ext
			))


# Article model

class Article(m.Model):
	created_by 			=	m.ForeignKey(to=user_cls,
								verbose_name="created user",
								related_name='articles',
								blank=True,
								null=False,
								on_delete=m.CASCADE)

	created_by_username =   m.CharField(max_length=255,
										verbose_name="created username",
										blank=True,
										null=True)

	title  				= m.CharField(max_length=120,verbose_name="article title",
						  	blank=False,
						  	null=False)
	
	slug 				=  	m.SlugField(max_length=200,verbose_name="title slug",
									allow_unicode=True,unique=True,blank=True,null=True)

	content 			=	m.TextField(max_length=450,verbose_name="content",blank=False,null=False)

	image 				=	m.ImageField(upload_to=article_cover_upload_dir,verbose_name="article image",max_length=255,blank=True,null=True)

	published_date 		=	m.DateTimeField(blank=True,null=True)

	is_edited_date 		=	m.DateTimeField(blank=True,null=True)

	status 				=	m.CharField(max_length=1,choices=ArticleStatus.CHOICES,default=ArticleStatus.P)


	board 				=	m.ForeignKey(to=Board,verbose_name="article board",
										on_delete=m.CASCADE,
										blank=True,
										null=False,
										related_name="articles")

	# how we delete articles `avoiding 404 error for deleted articles`
	is_deleted 			=	m.DateTimeField(blank=True,null=True,verbose_name="article is deleted on")

	views_counts 		=	m.PositiveIntegerField(verbose_name="viewers count",blank=True,null=True,default=0)

	likes_counts 		=	m.PositiveIntegerField(verbose_name="likes count",blank=True,null=True,default=0)

	comment_count 		=	m.PositiveIntegerField(verbose_name="comments count",blank=True,null=True,default=0)

	created_date 		=	m.DateTimeField(auto_now_add=True)

	modified_date		= 	m.DateTimeField(auto_now=True)

	tags 				=	TaggableManager()

	objects			    = 	ArticleQuerySet.as_manager()


	class Meta:
		verbose_name    =	"Blog Article"
		verbose_name_plural = "Blog Article's"


	def __str__(self):
		if self.title:
			return self.title
		return self.article_short_content()


	@tx.atomic
	def save(self,*args,**kwargs):
		super(self.__class__,self).save(*args,**kwargs)
		# update count - board & user
		self.board.update_last_article()


	def _delete(self):
		pass


	@tx.atomic
	def delete(self,*args,**kwargs):
		board = self.board
		super(self.__class__,self).delete(*args,**kwargs)
		# update count - board & user
		board.update_last_article()


	def get_absolute_url(self):
		return reverse('blog:article-view',args=[str(self.slug)])


	def article_short_content(self):
		content = self.content
		max_len_ = Dev.settings['article_summary_maximum_length']
		len_ = int(len(content) / 2 )

		if len(self.content) > max_len_:
			return Truncator(content).chars(max_len_)
		return Truncator(content).chars(len_)
		
	display_content = property(article_short_content)


	def article_readtime(self):
		return str(readtime.of_text(self.content))
	article_readtime = property(article_readtime)


	@classmethod
	def fetch_similar_articles_for_this_article(cls,article,number:int=5):
		# cache me!
		article_tags_ids = article.tags.values_list('id',flat=True)
		similar_articles = cls.objects.get_published_articles().select_related('created_by','board').\
		filter(tags__in=article_tags_ids).exclude(id=article.id)

		similar_articles = similar_articles.annotate(same_tags=Count('tags')).\
		order_by('-same_tags','-created_date')[:number]

		return similar_articles


	@property
	def get_article_image_or_default(self):
		# cache me!
		if self.image:
			return self.image.url
		return Dev.settings['default_article_cover_img']


	# @property
	# def timesince_published(self):
	# 	if not self.published_date is None:
	# 		return naturaltime(self.published_date)
	# 	return ""


	@property
	def timesince_published(self):
		# attempt to use humanize package, issues with offset-naive and offset-aware datetime
		# http://pytz.sourceforge.net/
		# https://pypi.org/project/humanize/
		import humanize
		
		timelapse = self.published_date.replace(tzinfo=None)
		return humanize.naturaltime(timelapse)
		

	# @property
	# def timesince_published(self):
	# 	import arrow
	# 	time_ = arrow.get(self.published_date)
	# 	return time_.humanize(granularity=["day"])

	@property
	def strformat_published_date(self):
		if not self.published_date is None: 
			return self.published_date.strftime("%b %d")
		return ""


	@property
	def strf_article_edited_date(self):
		if not self.is_edited_date is None:
			return self.is_edited_date.strftime("%b %d")
		return ""


	@property
	def is_editable(self):
		# limit article edit .
		if user := self.created_by:
			if timezone.now() < self.created_date + \
			 datetime.timedelta(minutes=Dev.settings['editable_timeout']):
				return True
		return False


	@property
	def incr_views(self):
		self.views_counts = F('views_counts') + 1
		self.save(update_fields=['views_counts'])
		self.refresh_from_db()
		# update board views count for every article view count
		self.board.update_views_count() 


	@property
	def incr_like(self):
		self.likes_counts = F('likes_counts') + 1
		self.save(update_fields=['likes_counts'])
		self.refresh_from_db()


	@property
	def decr_like(self):
		self.likes_counts = F('likes_counts') - 1
		self.save(update_fields=['likes_counts'])
		self.refresh_from_db()


	def article_likes_qs(self):
		Like = apps.get_model("like", "Like")
		content_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(Article)
		qs = Like.objects.filter(content_type=content_type, object_id=self.id).select_related("user")
		return qs

	
	@property
	def users_like(self): 
		# cache me! 10 sec.
		users = [like.user for like in self.article_likes_qs()]
		return users

	def comments_qs_excluding_replies(self):
		# cache me!
		return self.comments.exclude(reply_to_this__isnull=False).select_related('commented_by')

	@property
	def incr_comment(self):
		self.comment_count = F('comment_count') + 1
		self.save(update_fields=['comment_count'])
		self.refresh_from_db()

	@property
	def decr_comment(self):
		self.comment_count = F('comment_count') - 1
		self.save(update_fields=['comment_count'])
		self.refresh_from_db()





class ArticleEditLog(m.Model):
	""" Model class ArticleEditLog - Tracking Article edit change logs. """

	edited_by 			=	m.ForeignKey(to=user_cls,on_delete=m.SET_NULL,blank=True,null=True,related_name="+")

	article 			=	m.ForeignKey(to=Article,on_delete=m.CASCADE,blank=True,null=True)

	edited_by_username  = 	m.CharField(blank=True,null=True,max_length=255)

	edited_from  		= 	m.TextField(max_length=450,blank=True,null=True)

	edited_on 			=	m.DateTimeField(blank=True,null=True,default=timezone.now)

	edited_to 			= 	m.TextField(max_length=450,blank=True,null=True)

	created_date 		= 	m.DateTimeField(auto_now_add=True)


	class Meta:
		ordering = ["-id"]

	def get_article_edited_diff(self):
		import difflib
		return difflib.ndiff(self.edited_from.splitlines(), self.edited_to.splitlines())




class ArticleComment(m.Model):

    commented_by	 = m.ForeignKey(settings.AUTH_USER_MODEL, 
    								null=False, 
    								blank=False,
    								related_name="user_comments", 
    								on_delete=m.CASCADE)


    commented_on_article = m.ForeignKey(to=Article,
    									on_delete=m.SET_NULL,
    									related_name="comments",
    									blank=True,
    									null=True)

    reply_to_this        = m.ForeignKey("self",null=True,
    								blank=True,
    								related_name="replies_to_article_comments",
    								on_delete=m.SET_NULL)

    content 			 = m.TextField(max_length=450,blank=False,null=False)

    created_at 			 = m.DateTimeField(auto_now_add=True)

    updated_at 			 = m.DateTimeField(auto_now=True)


    class Meta:
    	verbose_name = "Comment"
    	verbose_name_plural = "Comments"
    	ordering = (("id"),) # latest

    def __str__(self):
    	if self.commented_on_article and not self.commented_on_article.title is None:
    		return "{} commented".format(self.commented_by.username,self.commented_on_article.title)
    	return "{} made a comment on an article ".format(self.commented_by.username)

    def save(self,*args,**kwargs):
    	super().save(*args,**kwargs)





# class HitCount(m.Model):
# Celery-Beats call UserHitCount.calculate() every 6 hours
# use in views : user_ranking = HitRanking.objects.order_by("-count")[:8]


#     user = m.ForeignKey(to=user_cls, related_name="hit_count", on_delete=m.CASCADE)
#     count = m.PositiveIntegerField(default=0)

#     @classmethod
#     def calculate(cls):
#         User = user_cls()
#         for user in User.objects.all():
#             articles_count = [Article_model].objects.filter(created_by=user).count()
#             comments_count = [Comment_model].objects.filter(user=user).count()
#             likes_count = [Like_model].objects.filter(user=user).count()
#			  questions_count = [Question_model].objects.filter(user=user).count()
# 			  answers_count = [Answer_model].objects.filter(user=user).count()
#             count = articles_count + comments_count + likes_count + answers_count + questions_count
#             upc, created = cls._default_manager.get_or_create(
#                 user=user,
#                 defaults=dict(
#                     count=count
#                 )
#             )
#             if not created:
#                 upc.count = count
#                 upc.save()
# Python imports
import logging

# Django imports
from django.conf import settings
from django.utils import timezone
from django.db import transaction as tx
from django.http import HttpResponse,Http404,JsonResponse
from django.shortcuts import redirect,get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse


# Third Party imports
from taggit.models import Tag

# Project imports
from dev.core.decorators import ajax_required
from dev.users.models import Online
from dev.core.tasks import test_celery_func
from dev.core.utils.ip import client_ip_address
from ..like import services
from ..models import Article,Board,ArticleComment
from ..signals import article_is_viewed,article_is_edited
from ..forms import ArticleCreateForm,ArticleEditForm,CommentForm



logger = logging.getLogger(__name__)



@login_required
def article_lists(request,template="blog/article_lists.html",**kwargs):
	
	# GET sort in search.
	sort_by = request.GET.get("sort",None)

	def get_required_order(sort_by):

		default_order = "-published_date"

		if sort_by == "newest":
			return default_order
		elif sort_by == "oldest":
			return "published_date"
		return default_order

	# test-celery-working?
	test_celery_func.delay()

	show_welcome_message = False

	if request.session.has_key("is_new_user"):
		show_welcome_message = True
		del request.session["is_new_user"]

	sort = get_required_order(sort_by) # sort

	article_qs = Article.objects.get_currently_published_articles(sort).select_related('created_by','board')

	# board ranking
	board_qs_by_views = Board.objects.boards_ranking_by_viewed_counts()
	board_qs_by_articles_count = Board.objects.boards_rank_by_articles_counts()

	# common tags in Article Model : Article.tags.most_common()
	# common_tags_in_all_articles = Article.tags.most_common()[:5]

	template_data = {
	'article_qs':article_qs,
	'board_qs':board_qs_by_views,
	'board_qs_by_articles_count':board_qs_by_articles_count,
	'show_welcome_message':show_welcome_message,
	}

	return TemplateResponse(request,template,template_data)



@login_required
def article_view(request,template_name = "blog/article.html",**kwargs):
	article_qs = Article.objects.select_related('created_by','board')

	# cache me!
	article = article_qs.get(slug__iexact=kwargs.get('article_slug'))

	# cache me!
	similar_articles = Article.fetch_similar_articles_for_this_article(article)

	article_comments = article.comments_qs_excluding_replies()
	article_comments_count = article.comment_count


	comment_form = CommentForm()

	template_data = {
	"article":article,
	"similar_articles":similar_articles,
	"comment_form":comment_form,
	"article_comments":article_comments,
	"article_comments_count":article_comments_count,
	}

	# Signal : article-viewed signal
	article_is_viewed.send(sender=None,article=article,request=request)

	return TemplateResponse(request,template_name,template_data)



@login_required
def article_tag(request,tag_slug,template_name = "blog/article_tags.html",**kwargs):

	tag = get_object_or_404(Tag,slug=tag_slug)

	article_qs = Article.objects.filter(tags__id__in=[tag.id])

	template_data = {
	"tag":tag,
	"article_qs":article_qs,
	}
	
	return TemplateResponse(request,template_name,template_data)



@login_required
def article_edit(request,article_slug,template_name="blog/article_edit.html",**kwargs):
	article_qs = Article.objects.all() # including drafted aricles.
	article = get_object_or_404(article_qs,slug=str(article_slug))

	board = article.board

	is_published = bool(article.published_date)

	form = ArticleEditForm(instance=article,board=board,request=request)

	if request.method == 'POST':
		form = ArticleEditForm(instance=article,board=board,request=request,data=request.POST,files=request.FILES)
		if form.is_valid():
			article,is_publishing = form.save()
			# Signal article edited
			article_is_edited.send(sender=None,article=article)
			if is_publishing:
				# request-user in article users liked lists.
				if not request.user in article.users_like:
					services.switch_like(article,user=request.user) 
				built_url = reverse('blog:article-view',kwargs={'article_slug':article.slug})
				return redirect(built_url)
			else:
				logger.info("drafted article saved")
				return redirect(reverse('blog:board-view',kwargs={'board_slug':board.slug}))
		else:
			print("invalid data")
	template_data = {
		"form":form,
		"is_published":is_published,
	}

	return TemplateResponse(request,template_name,template_data)



@login_required
@require_http_methods(['POST'])
def article_delete(request,article_slug,**kwargs):
	article_qs = Article.objects.all()
	article = get_object_or_404(article_qs,slug=article_slug)

	print("article._delete called!")

	built_url = reverse('blog:article-view',kwargs={'article_slug':article.slug})

	return redirect(built_url)



@ajax_required
@login_required
@require_http_methods(['POST'])
def article_like(request):

	article = Article.objects.get(id=int(request.POST["id"]))

	# Like article
	is_liked = services.switch_like(article,user=request.user)

	data = {
	"is_liked":is_liked,
	"counts":article.likes_counts,
	}
	return JsonResponse(data,status=200)



@login_required
def board_view(request,board_slug,template_name='blog/article_create_board.html'):

	# cache
	board = get_object_or_404(Board,slug__exact=board_slug)
	
	# cache
	board_articles_qs = Board.objects.get_a_board_article_qs(board.id)

	article_create_form = ArticleCreateForm(board=board,request=request)

	user_drafted_articles_for_board = Article.objects.user_drafted_articles_in_this_board(request.user,board)

	# request.user drafted articles.
	# remove line 217 : making use of user_drafted articles context processors.
	user_drafts = Article.objects.user_drafted_articles(request.user).order_by('-created_date')


	if request.method == "POST":
		article_create_form = ArticleCreateForm(board=board,request=request,data=request.POST,files=request.FILES)
		if article_create_form.is_valid():
			article,is_publishing = article_create_form.save()
			if is_publishing:

				services.switch_like(article,user=request.user) #auto-like own article

				built_url = reverse('blog:article-view',kwargs={'article_slug':article.slug})
				return redirect(built_url)
			else:
				logger.info("drafted article saved")
				return redirect(reverse('blog:board-view',kwargs={'board_slug':board_slug}))
		else:
			print("Error in-valid data")

	template_data = {
	"board":board,
	"article_create_form":article_create_form,
	"board_articles_qs":board_articles_qs,
	"user_drafts_articles":user_drafts,
	}

	return TemplateResponse(request,template_name,template_data)



def boards_lists(request,template_name="blog/boards_lists.html",**kwargs):
	# cache me!
	board_qs = Board.objects.select_related("last_article","last_article__created_by").all()


	template_data = {
	"board_qs":board_qs,
	}
	return TemplateResponse(request,template_name,template_data)
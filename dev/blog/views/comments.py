# Django imports
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404,redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.urls import reverse

# Project imports
from dev.core.decorators import ajax_required
from dev.blog.models import Article,ArticleComment
from dev.blog.forms import CommentForm,CommentEditForm,CommentReplyEditForm
from ..signals import comment_is_added,comment_is_deleted


@ajax_required
@login_required
@require_http_methods(['POST'])
def article_comment(request):
	# ToDo : validate comment content for length.
	content = request.POST.get('content')
	article = get_object_or_404(Article,id=request.POST.get('article-id'))
	replied_to_comment_with_id = request.POST.get('reply_id',None)

	comment = ArticleComment(
		commented_by=request.user,
		commented_on_article = article,
		content = content
	)

	is_a_reply = False

	# is a reply
	reply_to_comment = None
	if not replied_to_comment_with_id is None:
		reply_to_comment = ArticleComment._default_manager.get(id=int(replied_to_comment_with_id))
		comment.reply_to_this = reply_to_comment
		# print("`Parent` Comment ID : ",reply_to_comment.id)
		is_a_reply = True

	comment_form = CommentForm()

	html = ""

	try:

		comment.save()
		# print("Reply ID : ",comment.id)
		# Signal comment added
		comment_is_added.send(sender=None,article=comment.commented_on_article)
	except (IntegrityError,OperationalError):

		return JsonResponse({"status": "false", "message": "Sorry, There was an error saving your comment."}, status=500)

	# comment is a `parent comment` - render parent comment template.
	if not is_a_reply:
		html = render_to_string(
			template_name ="blog/helper/include_comment.html",
			context={"article":article,"comment":comment,'comment_form':comment_form},
			request=request
		)
		
	# comment is a reply `child comment` render reply template
	else:
		html = render_to_string(
			template_name ="blog/helper/include_reply.html",
			context={"reply":comment,"comment_reply_parent":reply_to_comment},
			request = request
		)

	count = article.comment_count

	data_dict = {"html_template":html,"is_a_reply":is_a_reply,"count":count}
		
	return JsonResponse(data=data_dict, safe=False,status=200)



def comment_delete(request,**kwargs):

	comment = ArticleComment.objects.get(id=int(kwargs["comment_id"]))

	template_name = "blog/comment_delete.html"

	template_data = {
	"comment":comment,
	}

	return 	TemplateResponse(request,template_name,template_data)



@login_required
@require_http_methods(['POST'])
def comment_delete_confirmation(request,**kwargs):

	comment = ArticleComment.objects.get(id=int(kwargs["comment_id"]))

	article = comment.commented_on_article

	# comment has replies : its a parent-comment
	replies = comment.replies_to_article_comments.exists()

	# if parent-comment has replies? - `True` then, delete all replies in parent comment
	if replies:
		for reply in comment.replies_to_article_comments.all():

			article = reply.commented_on_article

			reply.delete()

			# delete Signal
			comment_is_deleted.send(sender=None,article=article)

	# either  a parent comment or a reply-comment
	comment.delete()

	# delete-Signal
	comment_is_deleted.send(sender=None,article=article)

	built_url = reverse('blog:article-view',kwargs={'article_slug':article.slug})

	return 	redirect(built_url)



# Parent Comment - Edit 
@login_required
def comment_edit(request,**kwargs):

	comment = ArticleComment._default_manager.get(id=int(kwargs["comment_id"]))

	article = comment.commented_on_article

	comment_edit_form = CommentEditForm(comment=comment)

	if request.method == "POST":
		comment_edit_form = CommentEditForm(comment=comment,data=request.POST)
		if comment_edit_form.is_valid():
			# comment edit - is it a parent or child ?
			# Hint : reply_id
			ArticleComment._default_manager.filter(id=int(kwargs["comment_id"])).\
			update(content=request.POST["content"])
			built_url = reverse('blog:article-view',kwargs={'article_slug':article.slug})
			return redirect(built_url)
		else:
			pass
	template_name = 'blog/comment_edit.html'
	template_data = {
	"comment_edit_form":comment_edit_form,
	}
	return TemplateResponse(request,template_name,template_data)



# Reply - Edit
@login_required
def comment_reply_edit(request,**kwargs):

	comment = ArticleComment.objects.get(id=int(kwargs.get('reply_id')))

	article = comment.commented_on_article

	comment_edit_form = CommentReplyEditForm(comment=comment)

	if request.method == "POST":
		comment_edit_form = CommentReplyEditForm(comment=comment,data=request.POST)
		if comment_edit_form.is_valid():
			ArticleComment._default_manager.filter(id=int(kwargs.get('reply_id'))).\
			update(content=request.POST["content"])

			return redirect(reverse('blog:article-view',kwargs={'article_slug':article.slug}))
		else:
			pass

	template_name = 'blog/comment_reply_edit.html'
	template_data = {
	"comment_edit_form":comment_edit_form,
	}
	return TemplateResponse(request,template_name,template_data)



# Like

@ajax_required
@login_required
@require_http_methods(['POST'])
def like_comments(request):
	# Like action.
	return JsonResponse({"is_liked":True})
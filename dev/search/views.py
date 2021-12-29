from django.apps import apps
from django.db.models import Q
from django.shortcuts import render
from dev.core.decorators import ajax_required
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from dev.blog.models import Article,Board

model_cls = apps.get_model('users', 'User')  

# Create your views here.
@login_required
@ajax_required
def search_article(request):
	# ToDo: use Postgres Search for `full-text searching`. 

	import time 

	# query


	q = request.GET.get("q")

	qs = []

	is_article_type = True

	# Fetch from Article model.
	q_start = time.time() # start search

	qs = Article.objects.filter(
			Q(title__icontains=q) | Q(content__icontains=q) | Q(tags__name__icontains=q)
	).select_related("created_by").distinct()

	# Fetch from User model.
	if not qs.exists():
		qs = model_cls._default_manager.filter(
			Q(username__icontains=q) | Q(email__icontains=q) | Q(full_name__icontains=q)
		).distinct()

		is_article_type = False

	q_end = time.time() # end search


	# attempt to calculate : search time
	time_lapse = q_end - q_start

	time_lapse = time_lapse / 1000

	time_lapse = "{0:10.3f}".format(time_lapse * 10)

	time_lapse = 0.001 if float(time_lapse) == 0.000 else time_lapse # avoiding 0.000 

	html = render_to_string(
		template_name ="search/search_template.html",
		context={"qs":qs,"is_article_type":is_article_type,"search_time_out":time_lapse}
	)

	data_dict = {"html_template":html}



	return JsonResponse(data=data_dict, safe=False)




@login_required
@ajax_required
def search_boards(request):
	query = request.GET.get("q","").strip()

	boards_qs = Board.objects.filter(
		Q(title__icontains=query) | Q(description__icontains=query)
	).distinct()

	data = {}

	data_lists = []


	print("Board Queryset : ",boards_qs)

	if boards_qs.exists():
		for board in boards_qs:
			data["title"] = board.title

	return JsonResponse(data,safe=False)
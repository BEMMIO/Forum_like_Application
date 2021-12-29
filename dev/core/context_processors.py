from  django.conf import settings
from dev.blog.models import Article

def site_informations(request):
	""" Context processor for site - name and domain. """

	data = {
	"project_name":settings.PROJECT_NAME,
	"project_domain": settings.PROJECT_DOMAIN,
	}

	return data


def authenticated_user_data(request):
	""" Context processor for authenticated user's data : including notifications,articles """

	data = {}

	if request.user.is_authenticated:
		data = {
		"drafts_articles_qs":Article.objects.user_drafted_articles(request.user),
		}

	return data
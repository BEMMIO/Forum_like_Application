from django import template

register = template.Library()

@register.simple_tag
def like_counts(article):
	"""
	templates :
	{% like_tags %}

	use:

	{% like_counts article %}

	"""
	return len(article.users_like)


@register.simple_tag
def user_in_obj_liked(article,user):
	"""
	templates :
	{% like_tags %}

	use:

	{% user_in_obj_liked article request.user %}

	"""
	return bool(user in article.users_like)
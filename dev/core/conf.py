import collections
from appconf import AppConf
from django.conf import settings as _settings


class Dev(object):
	# dict
	settings = collections.OrderedDict()

	settings['editable_timeout'] = 5
	settings['default_article_cover_img'] = _settings.STATIC_URL + "img/default_cover_img.jpeg"
	settings['article_summary_maximum_length'] = 96
	settings["online_timeout"] = 5 #minutes
	settings["minimum_username_length"] = 4
	settings["maximum_username_length"] = 7

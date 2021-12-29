import importlib
from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dev.blog'


    def ready(self):
        # importlib.import_module('dev.blog.receivers')
        importlib.import_module('dev.blog.signals')


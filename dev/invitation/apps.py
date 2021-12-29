import importlib
from django.apps import AppConfig


class InvitationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dev.invitation'


    def ready(self):
        importlib.import_module('dev.invitation.receivers')

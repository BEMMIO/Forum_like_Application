from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dev.accounts'


    def ready(self):
        import dev.accounts.signals
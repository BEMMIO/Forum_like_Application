from django.apps import apps

User = apps.get_model('users', 'User') 
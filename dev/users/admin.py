from django.contrib import admin

from .models.users import User
from .models.online import Online

# Register your models here.
admin.site.register(User)
admin.site.register(Online)
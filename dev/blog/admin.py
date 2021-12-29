from django.contrib import admin

from .models import Article,Board,ArticleComment
# Register your models here.
admin.site.register(Article)
admin.site.register(Board)
admin.site.register(ArticleComment)


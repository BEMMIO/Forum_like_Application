from django.urls import path
from .views import search_article,search_boards

app_name = 'search'

urlpatterns = [
    # Article
    path('',search_article,name='search-article'),
    path('b/',search_boards,name='search-boards'),

]


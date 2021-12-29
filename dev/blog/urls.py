from django.urls import path
from .views import articles
from .views import comments

app_name = 'blog'

urlpatterns = [

    # Article
    path('articles/',articles.article_lists,name='article-lists'),
    path('article/<str:article_slug>/',articles.article_view,name='article-view'),
    path('article/<str:article_slug>/delete/',articles.article_delete,name='article-delete'),
    path('article/<str:article_slug>/edit/',articles.article_edit,name='article-edit'),
    path('tags/<str:tag_slug>/',articles.article_tag,name='tagged'),

    # Like
    path('like/',articles.article_like,name='like'),

    # Comment
    path('comment/',comments.article_comment,name='comments'),
    path('comment/<int:comment_id>/',comments.comment_delete,name='comments-delete'),
    path('comment/<int:comment_id>/edit/',comments.comment_edit,name='comment-edit'),
    path('comment/<int:reply_id>/<int:comment_id>/edit/',comments.comment_reply_edit,name='comment-reply-edit'),
    path('comment-confirmation/<int:comment_id>/',comments.comment_delete_confirmation,name='comments-confirmation'),

    # Comment-Like
    path('comment-like-unlike/',comments.like_comments,name='comment-like-unlike'),

    # Board
    path('board/<str:board_slug>/',articles.board_view,name='board-view'),
    path('boards/',articles.boards_lists,name='board-lists'),

]


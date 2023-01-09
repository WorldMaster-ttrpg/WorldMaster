from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ArticleList.as_view(), name='wiki_article_index'),
    path('article/<str:slug>', views.ArticleDetail.as_view(), name='wiki_article_detail'),
    path('history/<str:slug>', views.article_history, name='wiki_article_history'),
    path('add/article', views.add_article, name='wiki_article_add'),
    path('edit/article/<str:slug>', views.edit_article, name='wiki_article_edit'),
]

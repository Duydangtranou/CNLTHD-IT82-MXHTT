from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("categories", views.CategoryViewSet, 'category')
router.register("articles", views.ArticleViewSet, 'article')
router.register("article-post", views.ArticlePostViewSset, 'article-post')
router.register("users", views.UserViewSet, 'user')
router.register("comments", views.CommentViewSet, 'comment')

urlpatterns = [
    path('', include(router.urls)),
    path('oauth2-info/', views.AuthInfo.as_view())
]
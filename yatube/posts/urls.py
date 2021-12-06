# posts/urls.py

from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'group/empty_group/',
        views.posts_without_group,
        name='posts_without_group'
    ),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
]

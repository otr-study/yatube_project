# posts/urls.py

from django.urls import path

from . import views

app_name = 'posts'

""" Екатерина, не переживайте, когда будем работать над формами,
я доработаю форму группы, чтобы slug со значением 'epmpy_group'
невозможно было создать"""
urlpatterns = [
    path('', views.index, name='index'),
    path(
        'group/empty_group/',
        views.posts_without_group,
        name='posts_without_group'
    ),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
]

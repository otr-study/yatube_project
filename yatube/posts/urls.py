from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path(
        'group/empty_group/',
        views.Group_posts.as_view(),
        name='posts_without_group'
    ),
    path('group/<slug:slug>/', views.Group_posts.as_view(), name='group_list'),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path('create/', views.Post_create.as_view(), name='post_create'),
    path(
        'posts/<int:post_id>/edit/',
        views.Post_edit.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/comment',
        views.Add_comment.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/',
        views.Post_detail.as_view(),
        name='post_detail'
    ),
    path('follow/', views.Follow_index.as_view(), name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.Profile_follow.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.Profile_unfollow.as_view(),
        name='profile_unfollow'
    ),
]

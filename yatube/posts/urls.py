from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path(
        'group/empty_group/',
        views.GroupPosts.as_view(),
        name='posts_without_group'
    ),
    path('group/<slug:slug>/', views.GroupPosts.as_view(), name='group_list'),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path('create/', views.PostCreate.as_view(), name='post_create'),
    path(
        'posts/<int:post_id>/edit/',
        views.PostEdit.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.AddComment.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetail.as_view(),
        name='post_detail'
    ),
    path('follow/', views.FollowIndex.as_view(), name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollow.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollow.as_view(),
        name='profile_unfollow'
    ),
    path('authors/', views.ListAuthors.as_view(), name='authors'),
    path('search/', views.Search.as_view(), name='search'),
    path('posts/<int:post_id>/like/', views.PostLike.as_view(), name='like'),
    path(
        'followers/<str:username>/',
        views.ListFollowers.as_view(),
        name='list_followers'),
    path(
        'followings/<str:username>/',
        views.ListFollowings.as_view(),
        name='list_followings'),
]

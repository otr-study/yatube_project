from django.conf import settings
from django.db.models import Count, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Comment, Like, Post, User

POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 10)
AUTHORS_PER_PAGE = getattr(settings, 'AUTHORS_PER_PAGE', 12)


class PostListMixin:
    paginate_by = POSTS_PER_PAGE
    model = Post


class PostAuthorEqualUserMixin():
    def dispatch(self, request, post_id):
        self.edit_post = get_object_or_404(Post, pk=post_id)
        if self.edit_post.author != request.user:
            return redirect(
                reverse_lazy(
                    'posts:post_detail',
                    args=(self.edit_post.id,)
                )
            )
        return super().dispatch(request, post_id)


class AuthorsListMixin:
    template_name = 'posts/authors_list.html'
    paginate_by = AUTHORS_PER_PAGE
    model = User


def queryset_cur_user_likes(request):
    return Like.objects.filter(
        user__username=request.user.username,
        post=OuterRef('pk')
    )


def queryset_cur_user_comments(request):
    return Comment.objects.filter(
        author__username=request.user.username,
        post=OuterRef('pk')
    )


def queryset_user_follow_stats():
    return User.objects.filter(
        pk=OuterRef('pk')
    ).annotate(Count('follower'), Count('following'))

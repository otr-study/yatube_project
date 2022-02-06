from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, User

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
    paginate_by = AUTHORS_PER_PAGE
    model = User

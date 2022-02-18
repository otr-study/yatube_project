import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Like, Post, User
from .utils import (AuthorsListMixin, PostAuthorEqualUserMixin, PostListMixin,
                    queryset_cur_user_comments, queryset_cur_user_likes)

TEMPLATE_POST_CREATE = 'posts/create_post.html'


class Index(PostListMixin, ListView):
    template_name = 'posts/index.html'

    def get_queryset(self):
        cache_key = f'index_{self.request.user.username}'
        queryset = cache.get(cache_key)
        if queryset:
            return queryset
        q_cur_user_likes = queryset_cur_user_likes(self.request)
        q_cur_user_comments = queryset_cur_user_comments(self.request)
        queryset = Post.objects.select_related(
            'group', 'author'
        ).prefetch_related(
            'likes', 'comments'
        ).annotate(
            cur_user_like=Subquery(
                q_cur_user_likes.values('user')[:1]
            )
        ).annotate(
            cur_user_comment=Subquery(
                q_cur_user_comments.values('author')[:1]
            )
        )
        queryset = list(queryset)
        cache.set(cache_key, queryset, 20)
        return queryset


class Search(PostListMixin, ListView):
    template_name = 'posts/search.html'

    def get_queryset(self):
        self.query = self.request.GET.get('query')
        q_cur_user_likes = queryset_cur_user_likes(self.request)
        q_cur_user_comments = queryset_cur_user_comments(self.request)
        return Post.objects.select_related(
            'author', 'group'
        ).prefetch_related(
            'likes', 'comments'
        ).filter(
            Q(text__icontains=self.query) | Q(title__icontains=self.query)
        ).annotate(
            cur_user_like=Subquery(
                q_cur_user_likes.values('user')[:1]
            )
        ).annotate(
            cur_user_comment=Subquery(
                q_cur_user_comments.values('author')[:1]
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        return context


class GroupPosts(PostListMixin, ListView):
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        self.group = slug and get_object_or_404(Group, slug=slug)
        q_cur_user_likes = queryset_cur_user_likes(self.request)
        q_cur_user_comments = queryset_cur_user_comments(self.request)
        return Post.objects.select_related(
            'author'
        ).prefetch_related(
            'likes', 'comments'
        ).filter(
            group=self.group
        ).annotate(
            cur_user_like=Subquery(
                q_cur_user_likes.values('user')[:1]
            )
        ).annotate(
            cur_user_comment=Subquery(
                q_cur_user_comments.values('author')[:1]
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class Profile(PostListMixin, ListView):
    template_name = 'posts/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        q_cur_user_likes = queryset_cur_user_likes(self.request)
        q_cur_user_comments = queryset_cur_user_comments(self.request)
        return self.author.posts.select_related(
            'group'
        ).prefetch_related(
            'likes', 'comments'
        ).annotate(
            count_posts=Count('id')
        ).annotate(
            cur_user_like=Subquery(
                q_cur_user_likes.values('user')[:1]
            )
        ).annotate(
            cur_user_comment=Subquery(
                q_cur_user_comments.values('author')[:1]
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['following'] = self.author.following.filter(
            user_id=self.request.user.id
        ).exists()
        return context


class PostDetail(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        post.cur_user_like = Like.objects.filter(
            user__username=request.user.username,
            post=post
        ).exists()
        post.cur_user_comment = Comment.objects.filter(
            author__username=request.user.username,
            post=post
        ).exists()
        form = CommentForm()
        context = {
            'post': post,
            'form': form,
        }
        return render(request, 'posts/post_detail.html', context)


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = TEMPLATE_POST_CREATE

    def get_success_url(self):
        return reverse_lazy(
            'posts:profile',
            args=(self.request.user.username,)
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEdit(LoginRequiredMixin, PostAuthorEqualUserMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = TEMPLATE_POST_CREATE
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy(
            'posts:post_detail',
            args=(self.kwargs['post_id'],)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class AddComment(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
        return redirect('posts:post_detail', post_id=post_id)


class FollowIndex(LoginRequiredMixin, PostListMixin, ListView):
    template_name = 'posts/follow.html'

    def get_queryset(self):
        q_cur_user_likes = queryset_cur_user_likes(self.request)
        q_cur_user_comments = queryset_cur_user_comments(self.request)
        return Post.objects.filter(
            author__following__user=self.request.user
        ).select_related(
            'author', 'group'
        ).prefetch_related(
            'likes', 'comments'
        ).annotate(
            cur_user_like=Subquery(
                q_cur_user_likes.values('user')[:1]
            )
        ).annotate(
            cur_user_comment=Subquery(
                q_cur_user_comments.values('author')[:1]
            )
        )


class ProfileFollow(LoginRequiredMixin, View):
    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        follow_exist = author.following.filter(
            user_id=request.user.id
        ).exists()
        if (author != request.user and not follow_exist):
            Follow.objects.create(user=request.user, author=author)
        return redirect(
            reverse_lazy(
                'posts:profile',
                args=(author.username,)
            )
        )


class ProfileUnfollow(LoginRequiredMixin, View):
    def get(self, request, username):
        follows = Follow.objects.filter(
            user=request.user,
            author__username=username,
        )
        if follows.exists():
            follows.delete()
        return redirect(
            reverse_lazy(
                'posts:profile',
                args=(username,)
            )
        )


class ListAuthors(AuthorsListMixin, ListView):
    template_name = 'posts/authors_list.html'
    queryset = User.objects.annotate(
        posts_count=Count('posts')
    ).filter(posts_count__gt=0)


class PostLike(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = post.likes.filter(
            user_id=request.user.id
        )
        result = {}
        if like.exists():
            like.delete()
            result['result'] = False
        else:
            Like.objects.create(user=request.user, post=post)
            result['result'] = True
        result['count'] = post.likes.count()
        result['post_id'] = post_id
        return HttpResponse(json.dumps(result))

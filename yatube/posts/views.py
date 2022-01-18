from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, View

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import PostAuthorEqualUserMixin, PostListMixin

TEMPLATE_POST_CREATE = 'posts/create_post.html'


class Index(PostListMixin, ListView):
    template_name = 'posts/index.html'
    queryset = Post.objects.select_related(
        'group'
    ).select_related('author')

    @method_decorator(cache_page(20))
    def get(self, request):
        return super().get(request)


class GroupPosts(PostListMixin, ListView):
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        self.group = slug and get_object_or_404(Group, slug=slug)
        return Post.objects.select_related('author').filter(group=self.group)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class Profile(PostListMixin, ListView):
    template_name = 'posts/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return self.author.posts.select_related('group')

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
        form = CommentForm()
        context = {
            'post': post,
            'form': form,
        }
        return render(request, 'posts/post_detail.html', context)


class PostCreate(LoginRequiredMixin, View):
    def get(self, request):
        form = PostForm()
        return render(
            request,
            template_name=TEMPLATE_POST_CREATE,
            context={'form': form}
        )

    def post(self, request):
        form = PostForm(
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    args=(request.user.username,)
                )
            )
        return render(
            request,
            template_name=TEMPLATE_POST_CREATE,
            context={'form': form}
        )


class PostEdit(LoginRequiredMixin, PostAuthorEqualUserMixin, View):
    def get(self, request, post_id):
        form = PostForm(instance=self.edit_post)
        return render(
            request,
            template_name=TEMPLATE_POST_CREATE,
            context={'form': form, 'is_edit': True}
        )

    def post(self, request, post_id):
        form = PostForm(
            instance=self.edit_post,
            files=request.FILES or None,
            data=request.POST or None)
        if form.is_valid():
            form.save()
            return redirect(
                reverse_lazy(
                    'posts:post_detail',
                    args=(self.edit_post.id,)
                )
            )
        return render(
            request,
            template_name=TEMPLATE_POST_CREATE,
            context={'form': form, 'is_edit': True}
        )


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
        return Post.objects.filter(
            author__following__user=self.request.user
        ).select_related('author').select_related('group')


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

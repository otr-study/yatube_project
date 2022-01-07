from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import View

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import PostAuthorEaualUserMixin, get_paginator_page

TEMPLATE_POST_CREATE = 'posts/create_post.html'


class Index(View):
    @method_decorator(cache_page(20))
    def get(self, request):
        template = 'posts/index.html'
        posts = Post.objects.all()
        page_number = request.GET.get('page')
        page_obj = get_paginator_page(posts, page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, template, context)


class Group_posts(View):
    def get(self, request, slug=None):
        template = 'posts/group_list.html'
        group = slug and get_object_or_404(Group, slug=slug)
        posts = Post.objects.filter(group=group)
        page_number = request.GET.get('page')
        page_obj = get_paginator_page(posts, page_number)
        context = {
            'group': group,
            'page_obj': page_obj,
        }
        return render(request, template, context)


class Profile(View):
    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        following = author.following.filter(user_id=request.user.id).exists()
        posts = author.posts.all()
        page_number = request.GET.get('page')
        page_obj = get_paginator_page(posts, page_number)
        context = {
            'author': author,
            'page_obj': page_obj,
            'following': following,
        }
        return render(request, 'posts/profile.html', context)


class Post_detail(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm()
        context = {
            'post': post,
            'form': form,
        }
        return render(request, 'posts/post_detail.html', context)


class Post_create(LoginRequiredMixin, View):
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


class Post_edit(LoginRequiredMixin, PostAuthorEaualUserMixin, View):
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


class Add_comment(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
        return redirect('posts:post_detail', post_id=post_id)


class Follow_index(LoginRequiredMixin, View):
    def get(self, request):
        posts = Post.objects.filter(author__following__user=request.user)
        page_number = request.GET.get('page')
        page_obj = get_paginator_page(posts, page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'posts/follow.html', context)


class Profile_follow(LoginRequiredMixin, View):
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


class Profile_unfollow(LoginRequiredMixin, View):
    def get(self, request, username):
        follow = get_object_or_404(
            Follow,
            user=request.user,
            author__username=username,
        )
        follow.delete()
        return redirect(
            reverse_lazy(
                'posts:profile',
                args=(username,)
            )
        )

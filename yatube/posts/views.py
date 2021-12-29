from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import CommentForm, PostForm
from .models import Group, Post, User
from .utils import get_paginator_page

TEMPLATE_POST_CREATE = 'posts/create_post.html'
TEMPLATE_GROUP_LIST = 'posts/group_list.html'


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_number = request.GET.get('page')
    page_obj = get_paginator_page(posts, page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = get_paginator_page(posts, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, TEMPLATE_GROUP_LIST, context)


def posts_without_group(request):
    posts = Post.objects.filter(group=None)
    page_number = request.GET.get('page')
    page_obj = get_paginator_page(posts, page_number)
    context = {
        'group': None,
        'page_obj': page_obj,
    }
    return render(request, TEMPLATE_GROUP_LIST, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_number = request.GET.get('page')
    page_obj = get_paginator_page(posts, page_number)
    context = {
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None
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


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, pk=post_id)
    if edit_post.author != request.user:
        return redirect(
            reverse_lazy(
                'posts:post_detail',
                args=(edit_post.id,)
            )
        )
    form = PostForm(
        instance=edit_post,
        files=request.FILES or None,
        data=request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(
            reverse_lazy(
                'posts:post_detail',
                args=(edit_post.id,)
            )
        )
    return render(
        request,
        template_name=TEMPLATE_POST_CREATE,
        context={'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

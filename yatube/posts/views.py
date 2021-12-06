from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Group, Post, User

TEMPLATE_POST_CREATE = 'posts/create_post.html'


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def posts_without_group(request):
    template = 'posts/group_list.html'
    posts = Post.objects.filter(group=None)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': None,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
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

    form = PostForm()
    return render(
        request,
        template_name=TEMPLATE_POST_CREATE,
        context={'form': form}
    )


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(instance=edit_post, data=request.POST)
        if form.is_valid:
            form.save()
            return redirect(
                reverse_lazy(
                    'posts:profile',
                    args=(request.user.username,)
                )
            )
        return render(
            request,
            template_name=TEMPLATE_POST_CREATE,
            context={'form': form, 'is_edit': True}
        )
    form = PostForm(instance=edit_post)
    return render(
        request,
        template_name=TEMPLATE_POST_CREATE,
        context={'form': form, 'is_edit': True}
    )

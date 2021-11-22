from django.shortcuts import get_object_or_404, render

from .models import Group, Post

TEMPLATE_GROUP_LIST = 'posts/group_list.html'


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()[:10]
    context = {
        'posts': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:10]
    context = {
        'group': group,
        'posts': posts
    }
    return render(request, TEMPLATE_GROUP_LIST, context)


def posts_without_group(request):
    posts = Post.objects.filter(group=None)[:10]
    context = {
        'group': None,
        'posts': posts
    }
    return render(request, TEMPLATE_GROUP_LIST, context)

from django import template
from posts.models import Post

register = template.Library()

URLS_WITH_POP_ARTICLE = (
    'posts:index',
    'posts:posts_without_group',
    'posts:group_list',
    'posts:profile',
    'posts:post_detail',
    'posts:follow_index',
    'posts:authors',
)


@register.inclusion_tag('posts/popular_articles.html')
def popular_articles(request):
    render = request.resolver_match.view_name in URLS_WITH_POP_ARTICLE
    pop_posts = []
    if render:
        pop_posts = Post.objects.all()[:10]
    return {
        'pop_posts': pop_posts,
        'render': render,
    }

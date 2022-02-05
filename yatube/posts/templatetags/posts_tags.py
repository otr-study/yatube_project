from django import template
from posts.models import Post

register = template.Library()


@register.inclusion_tag('posts/popular_articles.html')
def popular_articles():
    pop_posts = Post.objects.all()[:10]
    return {'pop_posts': pop_posts}

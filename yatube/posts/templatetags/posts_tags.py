import datetime

from django import template
from django.core.cache import cache
from django.db.models import Count
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
    'posts:search',
)


@register.inclusion_tag('posts/popular_articles.html')
def popular_articles(request):
    render = (request.user_profile['use_pop_article']
              and request.resolver_match.view_name in URLS_WITH_POP_ARTICLE)
    pop_posts = []
    query = ('SELECT COUNT("posts_like"."id") AS "count_like", '
             '"posts_post"."id", "posts_post"."title", "posts_post"."pub_date", '
             '"posts_post"."author_id", "posts_post"."group_id", '
             '"auth_user"."username", "auth_user"."first_name", '
             '"auth_user"."last_name", "users_userprofile"."image", '
             '"posts_group"."id", "posts_group"."title", "posts_group"."slug" '
             'FROM "posts_like" INNER JOIN "posts_post" ON ("posts_like"."post_id" = "posts_post"."id") '
             'INNER JOIN "auth_user" ON ("posts_post"."author_id" = "auth_user"."id") '
             'LEFT OUTER JOIN "users_userprofile" ON ("auth_user"."id" = "users_userprofile"."user_id") '
             'LEFT OUTER JOIN "posts_group" ON ("posts_post"."group_id" = "posts_group"."id") '
             'WHERE "posts_post"."pub_date" BETWEEN %s AND %s '
             'GROUP BY "posts_post"."id", "posts_post"."title", "posts_post"."pub_date", "posts_post"."author_id", "posts_post"."group_id", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "users_userprofile"."image", "posts_group"."id", "posts_group"."title", "posts_group"."slug" '
             'ORDER BY "count_like" DESC  '
             'LIMIT 10')
    if render:
        pop_posts = cache.get('pop_posts')
        if not pop_posts:
            now = datetime.datetime.now()
            month_ago = now - datetime.timedelta(days=30)
            pop_posts = Post.objects.raw(
                query, [month_ago, now]
            )
            cache.set('pop_posts', pop_posts, 20)

    return {
        'pop_posts': pop_posts,
        'render': render and len(pop_posts),
    }

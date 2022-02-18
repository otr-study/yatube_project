from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def user_repr(user):
    return user.get_full_name() or user.get_username()


@register.filter
def current_user_like(post):
    if not post.cur_user_like:
        return 'article-middle__stats-heart'

    return 'article-middle__stats-heart article-middle__stats-heart_solid'


@register.filter
def current_comment_like(post):
    if not post.cur_user_comment:
        return 'article-middle__stats-message'

    return 'article-middle__stats-message article-middle__stats-message_solid'

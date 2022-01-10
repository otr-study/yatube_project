from django.conf import settings
from django.contrib import admin

from .models import Comment, Follow, Group, Post

EMPTY_VALUE = getattr(settings, 'EMPTY_VALUE', '-')


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description'
    )
    empty_value_display = EMPTY_VALUE


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'post',
        'author',
        'created',
        'text',
    )
    search_fields = ('text',)
    list_filter = ('created',)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

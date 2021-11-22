from django.contrib import admin
from .models import Post, Group

EMPTY_VALUE = '-пусто-'


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


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)

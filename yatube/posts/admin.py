from django.contrib import admin

from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'pub_date',
        'text',
        'author',
        'group'
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'created',
        'text',
        'author',
        'post',
    )
    search_fields = (
        'author',
        'text',
        'post',
    )
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

from django.contrib import admin
from . import models


# Register your models here.

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'object_id', 'text', 'comment_time', 'user')


@admin.register(models.MessageBoard)
class MessageBoardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reply_to', 'comment_time', 'parent', 'body')

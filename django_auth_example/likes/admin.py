from django.contrib import admin
from .models import LikeCount, LikeRecord


# Register your models here.
@admin.register(LikeCount)
class LikeCount(admin.ModelAdmin):
    list_display = ('content_object', 'content_type', 'object_id', 'liked_num')


@admin.register(LikeRecord)
class LikeRecord(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'user')

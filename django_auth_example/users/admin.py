from django.contrib import admin
from . import models
from django.contrib.auth.models import User


# 博客分类
@admin.register(models.Category)
class BlogCategory(admin.ModelAdmin):
    list_display = ('name',)


# 博客标签
@admin.register(models.Tag)
class BlogTag(admin.ModelAdmin):
    list_display = ('name',)


# 博客文章
@admin.register(models.Post)
class BlogPost(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'get_read_num', 'create_time', 'modified_time')
    list_per_page = 10
    search_fields = ('author', 'title', 'excerpt')
    date_hierarchy = 'create_time'


# 公告
@admin.register(models.announcement)
class Announcement(admin.ModelAdmin):
    list_display = ('text', 'create_time')


# 分享编程文章
@admin.register(models.ShareProgram)
class KnowledgeShareProgram(admin.ModelAdmin):
    list_display = ('title', 'href', 'create_time')


# 分享其他文章
@admin.register(models.ShareOthers)
class KnowledgeShareOthers(admin.ModelAdmin):
    list_display = ('title', 'href', 'create_time')


# 分享标签
@admin.register(models.ShareTag)
class ShareTag(admin.ModelAdmin):
    list_display = ('tag_name', 'tag_text')


# @admin.register(models.Views)
# class BlogViews(admin.ModelAdmin):
#     list_display = ('read_num', 'post')


# @admin.register(models.ReadDetail)
# class BlogReadDetail(admin.ModelAdmin):
#     list_display = ('read_num', 'post', 'object_id', 'date')

admin.site.site_title = '博客管理系统'
admin.site.site_header = '欢迎使用博客管理系统'

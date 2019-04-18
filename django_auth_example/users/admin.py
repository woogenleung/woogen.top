from django.contrib import admin
from . import models
from django.contrib.auth.models import User


# Register your models here.

class Post_model(admin.ModelAdmin):
    list_display = ('title', 'create_time', 'excerpt', 'author')
    list_per_page = 10
    search_fields = ('author', 'title', 'excerpt')
    date_hierarchy = 'create_time'


admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Post, Post_model)
admin.site.site_title = '博客管理系统'
admin.site.site_header = '欢迎使用博客管理系统'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..models import Post, Category, Tag, announcement, ShareProgram, ShareOthers
from django import template
from django.db.models.aggregates import Count

register = template.Library()

# 获取最新的文章
@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-create_time')[:num]


# 获取日期
@register.simple_tag
def archives():
    return Post.objects.dates('create_time', 'month', order='DESC')


# 获取分类
@register.simple_tag
def get_categories():
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


# 获取所有标签
@register.simple_tag
def get_tags():
    return Tag.objects.all()

# 获取最新的公告
@register.simple_tag
def get_announcement():
    return announcement.objects.order_by('-create_time')[0]


# 获取分享的编程文章
@register.simple_tag
def get_ShareProgram():
    return ShareProgram.objects.all()

# 获取分享的其他文章
@register.simple_tag
def get_ShareOthers():
    return ShareOthers.objects.all()



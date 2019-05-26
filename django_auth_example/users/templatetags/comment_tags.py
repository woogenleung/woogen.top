#!/usr/bin/env python
# -*- coding: utf-8 -*-
from comment.models import Comment
from comment.forms import CommentForm
from django import template
from django.db.models.aggregates import Count
from django.contrib.contenttypes.models import ContentType

register = template.Library()


# 文章评论数
@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comment_count = Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()
    return comment_count


# 评论form(评论框)
@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    commnet_form = CommentForm(initial={
        'content_type': content_type.model,
        'object_id': obj.pk,
        'reply_comment_id': 0})
    return commnet_form


# 评论列表
@register.simple_tag
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent_id=None)
    return comments.order_by('-comment_time')

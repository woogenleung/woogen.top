#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'comment'
urlpatterns = [
    url(r'^update_comment', views.update_comment, name='update_comment'),
    url(r'^message_board', views.message_board, name='message_board'),
    # 二级回复
    url(r'^messageboard/(?P<parent_comment_id>[0-9]+)', views.messageboard, name='reply_comment'),
    # 一级评论
    url(r'^messageboard', views.messageboard, name='post_comment'),
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from . import views
from django.views.static import serve
from django_auth_example import settings

app_name = 'blog'
urlpatterns = [
    url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.archives, name='archives'),
    url(r'^tags/(?P<tag_name>.*?)/$', views.tags, name='tags'),
    url(r'^category/(?P<category_name>.*?)/$', views.category, name='category'),
    url(r'^bloglist/', views.bloglist, name='bloglist'),
    url(r'^knowledge/$', views.knowledge, name='knowledge'),
    url(r'^about/$', views.about, name='about'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', views.index, name='index'),
]

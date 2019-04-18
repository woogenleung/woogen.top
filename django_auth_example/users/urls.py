#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^blog/$', views.index, name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.archives, name='archives'),
    url(r'^tags/(?P<tag_name>.*?)/$', views.tags, name='tags'),
    url(r'^about/$', views.about, name='about'),
]

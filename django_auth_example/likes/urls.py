#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = 'like'
urlpatterns = [
    url(r'^like_change', views.like_change, name='like_change'),
]

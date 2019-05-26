#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'user'
urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^ChangeNickname', views.change_nickname, name='ChangeNickname'),
    url(r'^forget_pwd/$', views.modify_pwd, name='modify_pwd'),
    url(r'^ajax_captcha/', views.ajax_captcha, name='ajax_captcha'),
    url(r'^captcha_refresh', views.captcha_refresh, name='captcha_refresh'),
    url(r'^user_info', views.user_info, name='user_info'),
    url(r'^bind_email', views.bind_email, name='bind_email'),
    url(r'^ChangePassword', views.change_password, name='ChangePassword'),
    url(r'^send_verification_code', views.send_verification_code, name='send_verification_code'),
    url(r'^user_confirm', views.user_confirm, name='user_confirm'),
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField
from django.contrib import auth
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''}))
    password = forms.CharField(max_length=258, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'}, )

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''}))
    username = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(min_length=6, max_length=258,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    password2 = forms.CharField(
        min_length=6,
        max_length=258,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    verification_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            print('用户')
            raise forms.ValidationError('用户已存在')
        else:
            return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            print('邮箱')
            raise forms.ValidationError('邮箱已存在')
        else:
            return email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            print('密码')
            raise forms.ValidationError('两次输入的密码不一致')
        else:
            return password2


class ModifypwdForm(forms.Form):
    email = forms.EmailField(
        max_length=256,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    verification_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control user_code'})

    )

    password = forms.CharField(
        min_length=6,
        max_length=258,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ModifypwdForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            return email
        else:
            raise forms.ValidationError('邮箱不存在')

    def clean_verification_code(self):
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data


class ChangeNicknameForm(forms.Form):
    new_nickname = forms.CharField(
        max_length=20,
        label='新的昵称',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '请输入新的昵称', }
        )
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_new_nickname(self):
        new_nickname = self.cleaned_data.get('new_nickname', '').strip()
        if new_nickname == '':
            forms.ValidationError('新的昵称不能为空')
        return new_nickname


class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"获取'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断是否绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已绑定邮箱')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='旧的密码',
        min_length=6,
        max_length=36,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入旧密码'})
    )
    new_password = forms.CharField(
        label='新的密码',
        min_length=6,
        max_length=36,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入6-36位密码'})
    )
    confirm_password = forms.CharField(
        label='再输一次',
        min_length=6,
        max_length=36,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '重复新密码确保正确'})
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        new_password = self.cleaned_data.get('new_password', '')
        confirm_password = self.cleaned_data.get('confirm_password', '')
        if new_password != confirm_password or new_password == '':
            raise forms.ValidationError('两次密码不一致')

        return self.cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password

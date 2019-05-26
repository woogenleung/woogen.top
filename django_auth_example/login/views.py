import random
import time
import string
import datetime
import pytz
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import auth
from . import forms
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import Http404, HttpResponseRedirect
from .models import Profile, ConfirmString
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings


def login(request):
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    next = request.GET.get('next', '')
    print(next)
    if request.method == 'POST':
        next = request.POST.get('next', '')
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            if next == '':
                print('1')
                return HttpResponseRedirect(reverse('blog:index'))
            else:
                print('2')
                return HttpResponseRedirect(next)

            # username = login_form.cleaned_data.get('username')
            # password = login_form.cleaned_data.get('password')
            # # 账号登录
            # user = auth.authenticate(request, username=username, password=password)
            # if user is not None:
            #     auth.login(request, user)
            #     return redirect(referer)
            # else:
            #     message = '用户或密码不正确'
            #     return render(request, 'blog/login.html', locals())
        else:
            return render(request, 'blog/login.html', locals())
    login_form = forms.LoginForm()
    return render(request, 'blog/login.html', locals())


def register(request):
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            email = register_form.cleaned_data['email']
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password2']
            user = User.objects.create_user(username, email, password)
            user.save()
            code = make_confirm_string(user)
            # user = auth.authenticate(username=username, password=password)
            # auth.login(request, user)
            message = '注册'
            msg = '请前往注册邮箱,进行邮件确认'
            return render(request, 'blog/pagejump1.html', locals())
        else:
            return render(request, 'blog/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'blog/register.html', locals())


def logout(request):
    auth.logout(request)
    message = '退出'
    return render(request, 'blog/pagejump1.html', locals())
    # if not request.session.get('is_login', None):
    #     return redirect(reverse(('blog:index'), args=[]))
    # request.session.flush()
    # message = '退出'
    # return render(request, 'blog/pagejump.html', locals())


def modify_pwd(request):
    if request.method == 'POST':
        modifypwd_form = forms.ModifypwdForm(request.POST, request=request)
        if modifypwd_form.is_valid():
            email = modifypwd_form.cleaned_data['email']
            password = modifypwd_form.cleaned_data['password']
            verification_code = modifypwd_form.cleaned_data['verification_code']
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            message = '修改'
            msg = '请前往登录界面登录'
            return render(request, 'blog/pagejump1.html', locals())
        else:
            return render(request, 'blog/modify_pwd.html', locals())

    modifypwd_form = forms.ModifypwdForm()
    return render(request, 'blog/modify_pwd.html', locals())


# 动态验证
def ajax_captcha(request):
    if request.is_ajax():
        cs = CaptchaStore.objects.filter(response=request.GET['response'], hashkey=request.GET['hashkey'])
        if cs:
            json_data = {'status': 1}
        else:
            json_data = {'status': 0}
        return JsonResponse(json_data)
    else:
        raise Http404
        json_data = {'status': 0}
        return JsonResponse(json_data)


# 点击刷新
def captcha_refresh(request):
    if not request.is_ajax():
        raise Http404
    new_key = CaptchaStore.generate_key()
    json_data = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
    }
    return JsonResponse(json_data)


def user_info(request):
    return render(request, 'blog/user_info.html', locals())


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('blog:index'))
    if request.method == 'POST':
        form = forms.ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            new_nickname = form.cleaned_data['new_nickname']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = new_nickname
            profile.save()

            return redirect(redirect_to)
    else:
        form = forms.ChangeNicknameForm()
    context = {}
    context['title'] = '昵称'
    context['form_title'] = '修改昵称'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request, 'blog/user_form.html', context)


def change_password(request):
    redirect_to = request.GET.get('from', reverse('blog:index'))
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = forms.ChangePasswordForm()
    context = {}
    context['title'] = '密码'
    context['form_title'] = '修改密码'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request, 'blog/user_form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('blog:index'))
    if request.method == 'POST':
        form = forms.BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.has_confirmed = True
            profile.save()
            request.user.save()
            return redirect(redirect_to)
    else:
        form = forms.BindEmailForm()
    context = {}
    context['title'] = '邮箱'
    context['form_title'] = '绑定邮箱'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request, 'blog/send_mail.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 60:
            data['status'] = 'ERROR'
        else:
            request.session['bind_email_code'] = code
            request.session['send_code_time'] = now

            # 发送验证码
            send_mail(
                '邮箱验证|五更的个人博客',
                '验证码: %s' % code,
                '675839127@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def make_confirm_string(user):
    from uuid import uuid4
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    code = str(uuid4())
    ConfirmString.objects.create(code=code, user=user)
    return code


# 发送邮件
def send_email(email, code):
    title = '注册账号|五更的个人博客'
    html_content = '''
                            <p>感谢注册<a href="http://{}/user/user_confirm/?code={}" target=blank>woogen.top</a>，\
                            
                            <p>请点击站点链接完成注册确认！</p>
                            <p>此链接有效期为{}天！</p>
                            '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    email_from = '675839127@qq.com'
    receive = [
        email
    ]
    send_mail(title, html_content, email_from, receive, fail_silently=False)


# 确认邮箱
def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求'
        return render(request, 'blog/pagejump1.html', locals())
    create_time = confirm.create_time
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.timezone('UTC'))
    if now > create_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '你的邮件已过期,请重新注册'
        return render(request, 'blog/pagejump1.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '邮箱验证成功,请你尝试登陆吧!'
        return render(request, 'blog/pagejump1.html', locals())

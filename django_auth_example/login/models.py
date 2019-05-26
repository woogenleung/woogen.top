from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, verbose_name='昵称')
    has_confirmed = models.BooleanField(default=False, verbose_name='是否邮箱认证')
    header_image = models.ImageField(upload_to='media/img', default='media/img/touxiang.png', verbose_name='头像')

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)


class ConfirmString(models.Model):
    '''
    确认code类
    '''
    code = models.CharField(max_length=256)
    user = models.OneToOneField(User)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ':' + self.code

    class Meta:
        ordering = ['-create_time']
        verbose_name = '确认码'
        verbose_name_plural = '确认码'


def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username


def has_email_confirmed(self):
    profile = Profile.objects.get(user=self)
    if profile.has_confirmed:
        return profile.has_confirmed
    else:
        return ''


# def get_nickname(self):
#     if Profile.objects.filter(user=self).exists():
#         profile = Profile.objects.get(user=self)
#         return profile.nickname
#     else:
#         return ''
#
#
# def has_nickname(self):
#     return Profile.objects.filter(user=self).exists()
# User.get_nickname = get_nickname
# User.has_nickname = has_nickname

User.get_nickname_or_username = get_nickname_or_username
User.has_email_confirmed = has_email_confirmed

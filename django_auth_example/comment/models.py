import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.contrib.auth.models import User
# 多级评论模型
from mptt.models import MPTTModel, TreeForeignKey


class SendMail(threading.Thread):
    def __init__(self, msg):
        self.msg = msg
        threading.Thread.__init__(self)

    def run(self):
        self.msg.send()


class Comment(models.Model):
    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    # 评论是谁写的
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='', related_name='comments')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # 每条评论的根评论
    root = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='root_comment')
    # 每条评论的父评论,即被回复的那条评论
    parent_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING,
                                  related_name='parent_comment')
    # 回复谁
    reply_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def send_mail(self):
        # 发送邮件通知
        if self.parent_id is None:
            # 评论博客
            subject = 'woogen.top|有人评论你的博客'
            email = self.content_object.get_email()
        else:
            # 回复博客
            subject = 'woogen.top|有人回复你的评论'
            email = self.reply_to.email
        # 文本
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_absolute_url()
            # html_content = render(None, 'comment/send_mail.html', context).content.decode('utf-8')

            html_content = '''
                    <h3>有人回复了你的评论</h3>
                    <p>---------------------------------------</p>
                    {}
                    <p>---------------------------------------</p>
                    <p>请前往http://{}{} 查看回复</p>
                    <p>欢迎你的使用！</p>
                    '''.format(self.text, '127.0.0.1:8000', self.content_object.get_absolute_url())
            msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, [email])
            msg.content_subtype = 'html'
            msg_send = SendMail(msg)
            msg_send.start()
            # 另外一种方法
            # send_mail(subject, '', settings.EMAIL_HOST_USER, [email], fail_silently=False, html_message=html_content )

    def __str__(self):
        return self.text[:20]

    class Meta:
        ordering = ['-comment_time']
        verbose_name = '评论'
        verbose_name_plural = '评论'


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        order_with_respect_to = 'comment'


class Message(models.Model):
    username = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    text = models.TextField()
    url = models.URLField(null=True)


# 用mptt模型写留言板的多级评论
class MessageBoard(MPTTModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='MessageBoard_comments'
    )
    body = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    # mptt树形结构
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    # 二级评论
    reply_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='repliers'
    )

    class Meta:
        verbose_name = '留言板留言'
        verbose_name_plural = '留言板留言'
        ordering = ['-comment_time']

    class MPTTMeta:
        order_insertion_by = ['comment_time']

    def __str__(self):
        return self.body[:20]

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
# 多级评论模型
from mptt.models import MPTTModel, TreeForeignKey


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


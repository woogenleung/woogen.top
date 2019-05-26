import markdown
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from mdeditor.fields import MDTextField
from django.contrib.contenttypes.fields import GenericRelation
from read_statistics.models import ReadNumExpandMethod, ReadDetail


# Create your models here.

# 分类
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '博客文章类别'
        verbose_name_plural = '博客文章类别'


# 标签
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签云'
        verbose_name_plural = '标签云'


class Post(models.Model, ReadNumExpandMethod):
    # 文章名字
    title = models.CharField(max_length=70, verbose_name='文章标题')
    # 正文
    body = MDTextField(verbose_name='正文内容')
    # 创建时间
    create_time = models.DateTimeField(verbose_name='创建时间')
    # 最后一次修改时间
    modified_time = models.DateTimeField(verbose_name='最后修改时间')
    # 文章摘要
    excerpt = models.CharField(max_length=200, blank=True, verbose_name='文章摘要')
    # 展示图
    img = models.ImageField(upload_to='img', verbose_name='展示图', blank=True)
    # 一篇文章对应一个分类,可以有多个标签
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    read_detail = GenericRelation(ReadDetail)
    tag = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            self.excerpt = strip_tags(md.convert(self.body))[:150]
        super(Post, self).save(*args, **kwargs)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def get_email(self):
        return self.author.email

    class Meta:
        verbose_name = '博客文章'
        verbose_name_plural = '博客文章'
        ordering = ['-create_time']


class announcement(models.Model):
    text = models.TextField(max_length=256, verbose_name='公告内容')
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['create_time']
        verbose_name = '知识页公告'
        verbose_name_plural = '知识页公告'


class ShareTag(models.Model):
    tag_name = models.CharField(max_length=20, verbose_name='标签名字')
    tag_text = models.CharField(max_length=256, verbose_name='标签代码')
    tag_color = models.CharField(max_length=20, verbose_name='颜色代码')

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = '分享链接的标签样式'
        verbose_name_plural = '分享链接的标签样式'


class ShareProgram(models.Model):
    title = models.CharField(max_length=20, verbose_name='链接标题')
    href = models.URLField(verbose_name='链接')
    create_time = models.DateTimeField(auto_now_add=True)
    tag1 = models.ForeignKey(ShareTag, default='', related_name='Program_tag1', on_delete=models.CASCADE)
    tag2 = models.ForeignKey(ShareTag, default='', related_name='Program_tag2', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '分享的编程文章'
        verbose_name_plural = '分享的编程文章'


class ShareOthers(models.Model):
    title = models.CharField(max_length=20, verbose_name='链接标题')
    href = models.URLField(verbose_name='链接')
    create_time = models.DateTimeField(auto_now_add=True)
    tag1 = models.ForeignKey(ShareTag, default='', related_name='Others_tag1', on_delete=models.CASCADE)
    tag2 = models.ForeignKey(ShareTag, default='', related_name='Others_tag2', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '分享的其他文章'
        verbose_name_plural = '分享的其他文章'

# class Views(models.Model):
#     read_num = models.IntegerField(default=0, verbose_name='阅读量')
#     post = models.OneToOneField(Post, on_delete=models.DO_NOTHING, verbose_name='文章标题')
#
#     class Meta:
#         verbose_name = '阅读量'
#         verbose_name_plural = '阅读量'


# class ReadDetail(models.Model):
#     read_num = models.IntegerField(default=0)
#     date = models.DateField(default=timezone.now)
#     object_id = models.PositiveIntegerField()
#     post = models.ForeignKey(Post, on_delete=models.DO_NOTHING, verbose_name='文章标题')
#
#     class Meta:
#         verbose_name = '阅读详情'
#         verbose_name_plural = '阅读详情'

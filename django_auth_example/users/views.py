import markdown
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django_auth_example import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from read_statistics.utils import read_statistics_once_read, get_seven_days_read_data, get_seven_days_hot_data
from .models import Post, Tag, Category, ShareProgram, ShareOthers
from comment.models import Comment
from comment.forms import CommentForm


# 获取七天浏览记录和热门博客的缓存数据
def seven_blog():
    blog_content_type = ContentType.objects.get_for_model(Post)
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None:
        seven_days_hot_data = get_seven_days_hot_data()
        cache.set('seven_days_hot_data', seven_days_hot_data, 3600)
    date_nums = cache.get('date_nums')
    read_nums = cache.get('read_nums')
    if date_nums or read_nums is None:
        date_nums, read_nums = get_seven_days_read_data(blog_content_type)
        cache.set('date_nums', date_nums, 3600)
        cache.set('read_nums', read_nums, 3600)
    return seven_days_hot_data, read_nums, date_nums


# 装饰器,文章按列表,同时渲染分页栏.
def PageFun(func):
    def wrapper(*args, **kwargs):
        context = func(*args, **kwargs)
        blogs_all_list = context['blogs_all_list']
        request = context['request']
        blog_content_type = ContentType.objects.get_for_model(Post)
        # date_nums, read_nums = get_seven_days_read_data(blog_content_type)
        # 每6页进行分页
        paginator = Paginator(blogs_all_list, settings.Each_page_blogs)
        # 获取url的页码参数
        page_num = request.GET.get('page', 1)
        page_range = []
        try:
            contacts = paginator.page(page_num)
            # current_page_num = contacts.number
            # 获取当前页码前后2页范围
            page_range = [x for x in range(int(page_num) - 2, int(page_num) + 3) if 0 < x <= paginator.num_pages]
            if page_range[0] - 1 >= 2:
                page_range.insert(0, '...')
            if paginator.num_pages - page_range[-1] >= 2:
                page_range.append('...')
            # 加首尾页
            if page_range[0] != 1:
                page_range.insert(0, 1)
            if page_range[-1] != paginator.num_pages:
                page_range.append(paginator.num_pages)

        except PageNotAnInteger:
            contacts = paginator.page(1)
        except InvalidPage:
            return HttpResponse('找不到页面的内容')
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)
        seven_days_hot_data, read_nums, date_nums = seven_blog()
        context = {}
        context['post_list'] = contacts
        context['page_range'] = page_range
        context['read_nums'] = read_nums
        context['date_nums'] = date_nums
        context['seven_days_hot_data'] = seven_days_hot_data
        print(context)
        return render(request, 'blog/index.html', context)

    return wrapper


# 首页默认文章列表
@PageFun
def index(request):
    blogs_all_list = Post.objects.all().order_by('-create_time')
    context = {'request': request, 'blogs_all_list': blogs_all_list}
    return context


# 归档的文章列表
@PageFun
def archives(request, year, month):
    blogs_all_list = Post.objects.filter(create_time__year=year, create_time__month=month).order_by('-create_time')
    context = {'request': request, 'blogs_all_list': blogs_all_list}
    return context


# 标签的文章列表
@PageFun
def tags(request, tag_name):
    blogs_all_list = (Tag.objects.get(name=tag_name)).post_set.all().order_by('-create_time')
    context = {'request': request, 'blogs_all_list': blogs_all_list}
    return context


# 文章分类的文章列表
@PageFun
def category(request, category_name):
    blogs_all_list = (Category.objects.get(name=category_name)).post_set.all().order_by('-create_time')
    context = {'request': request, 'blogs_all_list': blogs_all_list}
    return context


# 文章详情页
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    blog_content_type = ContentType.objects.get_for_model(Post)
    # 阅读量增加
    read_cookie_key = read_statistics_once_read(request, post)
    seven_days_hot_data, read_nums, date_nums = seven_blog()
    post.body = markdown.markdown(
        post.body, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
    # comments = Comment.objects.filter(content_type=blog_content_type, object_id=post.pk, parent_id=None)
    context = {}
    context['post'] = post
    context['previous_blog'] = Post.objects.filter(create_time__gt=post.create_time).last()
    context['next_blog'] = Post.objects.filter(create_time__lt=post.create_time).last()
    context['read_nums'] = read_nums
    context['date_nums'] = date_nums
    context['seven_days_hot_data'] = seven_days_hot_data
    # 获取评论框和评论列表(现改成用自定义模板标签获取)
    # context['comments'] = comments
    # context['comment_form'] = CommentForm(initial={'content_type': blog_content_type.model, 'object_id': pk, 'reply_comment_id': 0})
    response = render(request, 'blog/single.html', context=context)
    response.set_cookie(read_cookie_key, 'true')
    return response


# 关于本人页
def about(request):
    return render(request, 'blog/about.html', locals())


# 知识页
def knowledge(request):
    return render(request, 'blog/knowledge.html', locals())


# 博客列表页(sf按哪种方式排序,st由多到少还是由少到多,category是否选择了分类)
def bloglist(request):
    sf = request.GET.get('sf', 'date')
    st = request.GET.get('st', '-1')
    category = request.GET.get('tag', '')
    print(sf + '--' + st + '--' + category)
    context = {}
    seven_days_hot_data, read_nums, date_nums = seven_blog()
    if category and category != 'all':
        # 如果选择了分类
        try:
            context['check_radio'] = category
            category = Category.objects.get(id=category)
            if sf == 'date':
                if st == '-1':
                    blogs_all_list = category.post_set.all().order_by('-create_time')
                    context['sorted_msg'] = '发布日期从近到远'
                else:
                    blogs_all_list = category.post_set.all().order_by('create_time')
                    context['sorted_msg'] = '发布日期从远到近'
            elif sf == 'view':
                if st == '-1':
                    blogs_all_list = category.post_set.all()
                    blogs_all_list = view_sort(blogs_all_list=blogs_all_list, reverse=True)
                    context['sorted_msg'] = '阅读数从多到少'

                else:
                    blogs_all_list = category.post_set.all()
                    blogs_all_list = view_sort(blogs_all_list=blogs_all_list, reverse=False)
                    context['sorted_msg'] = '阅读数从少到多'

            elif sf == 'comment':
                if st == '-1':
                    blogs_all_list = category.post_set.all()
                    blogs_all_list = comment_sort(blogs_all_list, reverse=True)
                    context['sorted_msg'] = '评论数从多到少'
                else:
                    blogs_all_list = category.post_set.all()
                    blogs_all_list = comment_sort(blogs_all_list, reverse=False)
                    context['sorted_msg'] = '评论数从少到多'
        except:
            blogs_all_list = {}
    else:
        # 没有选择分类,默认全部类别
        if sf == 'date':
            if st == '-1':
                blogs_all_list = Post.objects.all().order_by('-create_time')
                context['sorted_msg'] = '发布日期从近到远'
            else:
                blogs_all_list = Post.objects.all().order_by('create_time')
                context['sorted_msg'] = '发布日期从远到近'
        elif sf == 'view':
            if st == '-1':
                blogs_all_list = Post.objects.all()
                blogs_all_list = view_sort(blogs_all_list=blogs_all_list, reverse=True)
                context['sorted_msg'] = '阅读数从多到少'
            else:
                blogs_all_list = Post.objects.all()
                blogs_all_list = view_sort(blogs_all_list=blogs_all_list, reverse=False)
                context['sorted_msg'] = '阅读数从少到多'

        elif sf == 'comment':
            if st == '-1':
                blogs_all_list = Post.objects.all()
                blogs_all_list = comment_sort(blogs_all_list=blogs_all_list, reverse=True)
                context['sorted_msg'] = '评论数从多到少'
            else:
                blogs_all_list = Post.objects.all()
                blogs_all_list = comment_sort(blogs_all_list=blogs_all_list, reverse=False)
                context['sorted_msg'] = '评论数从少到多'
    # 分页器
    paginator = Paginator(blogs_all_list, settings.Each_page_blogs)
    # 获取url的页码参数
    page_num = request.GET.get('page', 1)
    page_range = []
    try:
        contacts = paginator.page(page_num)
        # 获取当前页码前后2页范围
        page_range = [x for x in range(int(page_num) - 2, int(page_num) + 3) if 0 < x <= paginator.num_pages]
        if page_range[0] - 1 >= 2:
            page_range.insert(0, '...')
        if paginator.num_pages - page_range[-1] >= 2:
            page_range.append('...')
        # 加首尾页
        if page_range[0] != 1:
            page_range.insert(0, 1)
        if page_range[-1] != paginator.num_pages:
            page_range.append(paginator.num_pages)

    except PageNotAnInteger:
        contacts = paginator.page(1)
    except InvalidPage:
        return HttpResponse('找不到页面的内容')
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    context['post_list'] = contacts
    context['page_range'] = page_range
    context['read_nums'] = read_nums
    context['date_nums'] = date_nums
    context['seven_days_hot_data'] = seven_days_hot_data
    return render(request, 'blog/blog_list.html', context)


def view_sort(blogs_all_list, reverse=True):
    data = {}
    for i in blogs_all_list:
        data[i] = i.get_read_num()
    sorted_dict = sorted(data.items(), key=lambda x: x[1], reverse=reverse)
    sorted_list = []
    for i in sorted_dict:
        sorted_list.append(i[0])
    blogs_all_list = sorted_list
    return blogs_all_list


def comment_sort(blogs_all_list, reverse=True):
    data = {}
    for post in blogs_all_list:
        content_type = ContentType.objects.get_for_model(post)
        comment_count = Comment.objects.filter(content_type=content_type, object_id=post.pk).count()
        data[post] = comment_count
    sorted_dict = sorted(data.items(), key=lambda x: x[1], reverse=reverse)
    sorted_list = []
    for i in sorted_dict:
        sorted_list.append(i[0])
    blogs_all_list = sorted_list
    return blogs_all_list

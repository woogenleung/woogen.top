from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Tag
import markdown
from comment.forms import CommentForm


# Create your views here.

def index(request):
    post_list = Post.objects.all().order_by('-create_time')
    return render(request, 'blog/index.html', locals())


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()
    post.body = markdown.markdown(
        post.body, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
        'post': post,
        'form': form,
        'comment_list': comment_list
    }
    return render(request, 'blog/single.html', context=context)


def archives(request, year, month):
    post_list = Post.objects.filter(create_time__year=year, create_time__month=month).order_by('-create_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


def tags(request, tag_name):
    post_list = (Tag.objects.get(name=tag_name)).post_set.all().order_by('-create_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})


def about(request):
    return render(request, 'blog/about.html', locals())

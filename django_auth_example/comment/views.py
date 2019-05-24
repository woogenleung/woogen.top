from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponse
from users.models import Post
from .models import Comment, MessageBoard
from .forms import CommentForm, MessageForm


def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('blog:index'))
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}

    if comment_form.is_valid():
        # 检查如果通过
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']
        parent_id = comment_form.cleaned_data['parent_id']
        if not parent_id is None:
            if parent_id.root is None:
                comment.root = parent_id
            else:
                comment.root = parent_id.root
            comment.parent_id = parent_id
            comment.reply_to = parent_id.user
        comment.save()

        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text
        if not parent_id is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        if not comment.root is None:
            data['root_pk'] = comment.root.pk
        else:
            data['root_pk'] = ''
        return JsonResponse(data)
    else:
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)


# 评论版页
def message_board(request):
    comment_form = MessageForm()
    comments = MessageBoard.objects.all()
    return render(request, 'blog/message_board.html', locals())


# 评论框的form
def messageboard(request, parent_comment_id=None):
    data = {}
    data['parent_id'] = parent_comment_id
    print(parent_comment_id)
    messageboard_form = MessageForm(request.POST, user=request.user)
    if request.method == 'POST':
        if messageboard_form.is_valid():
            new_comment = messageboard_form.save(commit=False)
            new_comment.user = messageboard_form.cleaned_data['user']
            data['reply_to'] = ''
            # 二级评论
            if parent_comment_id:
                print('二级评论')
                parent_comment = MessageBoard.objects.get(id=parent_comment_id)
                # 若回复超过二级,转换为二级
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()
                data['reply_to'] = parent_comment.user
                data['status'] = 'SUCCESS'
                data['message'] = '评论成功!'
                return JsonResponse(data)

            new_comment.save()
            data['id'] = new_comment.id
            data['username'] = new_comment.user.get_nickname_or_username
            data['comment_time'] = new_comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
            data['text'] = new_comment.body
            data['status'] = 'SUCCESS'
            data['message'] = '评论成功!'
            return JsonResponse(data)

        else:
            if messageboard_form.cleaned_data['message']:
                data['message'] = '用户尚未登录'
            else:
                data['message'] = '表单内容有误,请重新填写'
            data['status'] = 'ERROR'
            return JsonResponse(data)

    elif request.method == 'GET':
        messageboard_form = MessageForm()
        data['parent_id'] = parent_comment_id
        print(locals())
        return render(request, 'blog/reply.html', locals())
    else:
        return HttpResponse('仅接受GET/POST请求')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail
from users.models import Post


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 总阅读数 +1
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数 +1
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key


def get_seven_days_read_data(context_type):
    today = timezone.now().date()
    read_nums = []
    date_nums = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        date_nums.append(date.strftime('%m-%d'))
        read_details = ReadDetail.objects.filter(content_type=context_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return date_nums, read_nums


def get_seven_days_hot_data():
    today = timezone.now().date()
    print(today)
    date = today-datetime.timedelta(days=7)
    print(date)
    read_details = Post.objects.filter(read_detail__date__lt=today, read_detail__date__gte=date).values('id', 'title').annotate(read_num_sum=Sum('read_detail__read_num')).order_by('-read_num_sum')
    print(read_details)
    return read_details[:7]
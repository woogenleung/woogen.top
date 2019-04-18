from django.apps import AppConfig
import os

default_app_config = 'comment.CommentConfig'

def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]

class CommentConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = '评论管理'

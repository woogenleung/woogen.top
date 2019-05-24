"""django_auth_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import settings
from django.conf.urls.static import static

urlpatterns = [
                  url(r'^admin', admin.site.urls),
                  url(r'^user/', include('login.urls')),
                  url(r'captcha/', include('captcha.urls')),
                  url(r'^accounts/', include('allauth.urls')),
                  url(r'mdeditor/', include('mdeditor.urls')),
                  url(r'^ckeditor/', include('ckeditor_uploader.urls')),
                  url(r'comment/', include('comment.urls')),
                  url(r'like/', include('likes.urls')),
                  url(r'', include('users.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

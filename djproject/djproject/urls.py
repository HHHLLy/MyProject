"""djproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('news/',include('news.urls')),
    path('users/',include("users.urls")),
    path('',include("verifications.urls")),
    path('doc/',include('doc.urls')),
    path('course/',include('course.urls')),
    path('admin/',include('admin.urls')),
    path('qq/',include('qauth.urls')),
    re_path('media/(?P<path>.*)/',serve, {'document_root': settings.MEDIA_ROOT}),
    #可以用这种写法也可以用下面的来访问media

]
# ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)#需要拼接url来访问媒体文件


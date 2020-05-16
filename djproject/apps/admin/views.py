from datetime import datetime
from urllib.parse import urlencode
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.models import Group,Permission
from django.http import Http404

from users.models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse
import json
import logging
from doc.models import *
from django.http import FileResponse
import qiniu
from utils.qiniu_secret_info import *
from djproject import settings
from utils.fastdfs.fdfs import  FDFS_Client
from . import forms
from news.models import *
from course.models import *
from utils.res_codes import *
from utils.json_fun import *
from django.views import View

from .constants import *
# Create your views here.
from .scripts import paginator_script

logger = logging.getLogger('django')
class IndexView(LoginRequiredMixin,View):
    # login_url = 'login'
    redirect_field_name = 'next'

    def get(self,r):
        if not r.user.is_staff:
            return render(r,'403.html')
        return render(r,'admin/index/index.html')

class TagManagerView(PermissionRequiredMixin,View):
    permission_required = ('news.add_tag','news.view_tag')
    raise_exception = True
    def handle_no_permission(self):
        if self.request.method.lower() != 'get':

            return  to_json_data(errno=Code.UNKOWNERR,errmsg='没有操作权限')
        else:
            return super(TagManagerView,self).handle_no_permission()
    def get(self,r):
        tags = Tag.objects.values('id','name').\
            annotate(num_news = Count('news')).filter(
            is_delete=False
        ).order_by('-num_news','update_time')

        # rs = News.objects.filter(is_delete=False).annotate(num_comment=Count('comments')).\
        #     values('title','num_comment')
        # print(rs)

        return render(r,'admin/news/tag_manager.html',locals())
    def post(self,r):
        data = r.body
        if not data :
            return to_json_data(errno=Code.PARAMERR,errmsg='参数为空！')
        json_data = json.loads(data.decode('utf8'))
        name = json_data.get('name').strip(' ')
        if Tag.objects.filter(is_delete=False,name=name).exists() :
            return to_json_data(errno=Code.PARAMERR, errmsg='标签已存在！')
        tag = Tag.objects.filter(is_delete=True, name=name).first()
        if tag:
            tag.is_delete = False
            tag.save(update_fields = ['is_delete','update_time'])
            return to_json_data(errno=Code.OK)
        content , flag = Tag.objects.get_or_create(name=name)#如果存在就存 不存在就不存
        if flag:
            return to_json_data(errno=Code.OK)
        else:
            return to_json_data(errno=Code.PARAMERR,errmsg='添加失败')

class TagEditView(PermissionRequiredMixin,View):
    '''
          url: "/admin/tags/" + sTagId + "/",
    '''
    permission_required = ('news.delete_tag','news.change_tag')
    raise_exception = True
    def handle_no_permission(self):
        return to_json_data(errno=Code.ROLEERR,errmsg='您没有权限')
    def delete(self,r,tag_id):
       tag = Tag.objects.only('id').filter(id=tag_id).first()
       if  tag:
           tag.is_delete = True
           tag.save(update_fields = ['is_delete','update_time'])
           return to_json_data(errmsg='删除成功!')
       else:
           return  to_json_data(errno=Code.PARAMERR,errmsg='参数不存在！')
    def put(self,r,tag_id):
        data = r.body
        if not data :
            return to_json_data(errno=Code.PARAMERR, errmsg='参数不存在！')
        json_data = json.loads(data.decode('utf8'))
        tag_name = json_data.get('name')
        tag = Tag.objects.only("id").filter(id=tag_id,is_delete=False).first()
        if tag :
            if tag_name == tag.name:
                return to_json_data(errno=Code.PARAMERR,errmsg='标签未变化！')
            if Tag.objects.only('id').filter(name=tag_name).exists():
                return to_json_data(errno=Code.PARAMERR, errmsg='标签名称重复！')
            tag.name = tag_name.strip(' ')
            tag.save(update_fields=['name','update_time'])
            return to_json_data(errmsg="修改成功!")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='标签不存在！')
        # form = forms.TagEditForm(json_data,tag_id=tag_id)
        # if form.is_valid():
        #
        #     return to_json_data(errno=Code.OK)
        # else:
        #     error_msg_list = []
        #     for item in form.errors.get_json_data().values():
        #         error_msg_list.append(item[0].get('message'))
        #     error_list = ''.join(error_msg_list)

            # return to_json_data(errno=Code.PARAMERR,errmsg=error_list)



class HotNewsManagerView(PermissionRequiredMixin,View):
    permission_required = ('news.view_hotnews_')
    raise_exception = True
    def handle_no_permission(self):
        return to_json_data(errno=Code.ROLEERR, errmsg='您没有权限')
    def get(self,r):
        hot_news = HotNews.objects.select_related('news__tag').\
            only('news__title','news__tag__name','priority','news_id').\
            filter(is_delete=False).order_by('priority',"-update_time")[0:SHOW_HOSTNEWS_COUNT]
        # print(hot_news)
        return render(r,'admin/news/news_hot.html',locals())

class HotNewsEditView(PermissionRequiredMixin,View):
    permission_required = ('news.delete_hotnews','news.change_hotnews')
    raise_exception = True
    def handle_no_permission(self):
        return to_json_data(errno=Code.ROLEERR, errmsg='您没有权限')
    def delete(self,r,hn_id):
        hotnews = HotNews.objects.filter(is_delete=False,id=hn_id).first()
        if hotnews:
            hotnews.is_delete = True
            hotnews.save()
            return to_json_data(errno=Code.OK)
        else:
            return to_json_data(errno=Code.PARAMERR,errmsg='此热门文章不存在！')
    def put(self,r,hn_id):
        data = r.body
        if not data:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数不存在！')
        json_data = json.loads(data.decode('utf8'))

        try:
            priority = int(json_data.get('priority'))
            choice = [ i for i,_ in HotNews.PRI_CHOICE]

            if priority in choice:
                hotnews = HotNews.objects.filter(is_delete=False,id=hn_id).first()

                if hotnews:
                    if hotnews.priority == priority:
                        return to_json_data(errno=Code.PARAMERR, errmsg='热门文章优先级未修改！！')
                    hotnews.priority = priority
                    hotnews.save(update_fields=['priority','update_time'])
                    return to_json_data(errno=Code.OK)
                else:
                    return to_json_data(errno=Code.PARAMERR, errmsg='热门文章不存在！')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='此优先级不在选择范围！')

        except Exception as e:
            logger.info('热门文章优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR,errmsg='优先级修改异常')

class HotNewsAddView(PermissionRequiredMixin,View):
    permission_required = ('news.view_hotnews','news.add_hotnews')
    raise_exception = True
    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.UNKOWNERR, errmsg='没有操作权限')
        else:
            return super(HotNewsAddView, self).handle_no_permission()
    def get(self,r):
        tags = Tag.objects.values('id','name').annotate(num_news=Count('news')).filter(is_delete=False).\
            order_by('-num_news','update_time')
        priority_dict = dict(HotNews.PRI_CHOICE)
        return render(r,'admin/news/news_hot_add.html',locals())
    def post(self,r):
        data = r.body
        if not data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        json_data =json.loads(data.decode('utf8'))
        try:

            news_id = int(json_data.get('news_id'))
            if not  News.objects.filter(id=news_id,is_delete=False).exists():
                return to_json_data(errno=Code.PARAMERR,errmsg='没有此热门新闻！')
        except Exception as e:
            logger.info('获取ID参数错误.{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        try:

            priority = int(json_data.get('priority'))
            if not  priority in [i for i,_ in HotNews.PRI_CHOICE]:
                return to_json_data(errno=Code.PARAMERR,errmsg='没有此优先级！')
        except Exception as e:
            logger.info('获取优先级参数错误.{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # hotnews,flg = HotNews.objects.get_or_create(is_delete=False,news_id=news_id)
        hotnews = HotNews.objects.filter(is_delete=False,news_id=news_id).first()
        hotnews.priority = priority
        hotnews.save(update_fields=['priority','update_time'])
        return to_json_data(errmsg='保存成功！')

class HotNewsGetView(PermissionRequiredMixin,View):
    permission_required = ('news.view_news')
    raise_exception = True
    def handle_no_permission(self):
        return to_json_data(errno=Code.ROLEERR,errmsg="您没有权限")
    def get(self,r,tag_id):

        tag_news = News.objects.select_related('tag').values('title','id').\
            filter(is_delete=False,tag_id=tag_id)
        news = [i for i in tag_news]

        return to_json_data(data={'news':news})

class NewsManageView(PermissionRequiredMixin,View):
    permission_required = ('news.view_news')
    raise_exception = True


    def get(self,r):
        tags = Tag.objects.only('id','name').filter(is_delete=False)
        news = News.objects.select_related('author','tag'). \
            only('title','author__username','tag__name','update_time','id').filter(is_delete=False)
        start_time = r.GET.get('start_time','')
        end_time = r.GET.get('end_time', '')
        title = r.GET.get('title', '')
        author_name = r.GET.get('author_name', '')
        try:
            #字符串转时间
            datetime.strftime(start_time,'%Y/%m/%d') if start_time else ''
            datetime.strftime(end_time, '%Y/%m/%d') if end_time else ''
        except Exception as e:
            logger.info('用户输入的时间错误.{}'.format(e))
            start_time = end_time = ''
        news_list = news
        if start_time and not end_time:
            news_list = news.filter(update_time__gte=start_time)
        if not start_time and end_time:
            news_list = news.filter(update_time__lte=end_time)
        if start_time and end_time:
            news_list = news.filter(update_time__range=(start_time,end_time))
        # if not start_time and not end_time:
        #     news_list = news_list
        if title:
            news_list = news_list.filter(title__icontains=title)#模糊查询
        if author_name:
            news_list = news_list.filter(author__username__icontains=author_name)

        try:
            tag_id = int(r.GET.get('tag_id', 0))#有可能传非数字参数 所以用try
        except Exception as e:
            logger.info('标签参数错误.{}'.format(e))
            tag_id = 0
        if tag_id and tags.filter(id=tag_id).exists():
            news_list = news_list.filter(tag_id=tag_id)

        # 第二种写法 替换上面的if 如果标签存在但是标签下没有内容的情况下 要么不返回数据 要么返回所有数据
        # news_list = news_list.filter(is_delete=False,tag_id=tag_id) or news_list.filter(is_delete=False)

        try:
            page = int(r.GET.get('page'))
        except Exception as e:
            logger.info('当前页数错误.{}'.format(e))
            page = 1
        paginator = Paginator(news_list,PER_PAGE_NEWS_COUNT)
        try:
            news_info = paginator.page(page)
        except EmptyPage :
            logger.info('页码超过总共页数')
            news_info = paginator.page(paginator.num_pages)
        paginator_data = paginator_script.get_paginator_data(paginator, news_info)
        #时间转字符串
        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''
        context = {
            'news_info': news_info,
            'tags': tags,

            'start_time': start_time,
            "end_time": end_time,
            "title": title,
            "author_name": author_name,
            "tag_id": tag_id,
            "other_param": urlencode({
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "author_name": author_name,
                "tag_id": tag_id,
            })
        }
        context.update(paginator_data) #更新参数 把paginator_data添加进现在的context中
        return render(r,'admin/news/news_manage.html',context=context)

class NewsPubView(PermissionRequiredMixin,View):
    '''
    /admin/news/pub/
    '''
    permission_required = ('news.view_news','news.view_add')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(NewsPubView,self).handle_no_permission()
    def get(self,r):
        tags = Tag.objects.only('id','name').filter(is_delete=False)
        return render(r,'admin/news/news_pub.html',locals())
    def post(self,r):
        # tag 是以id进行存储
        if not r.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg="请从前端登录管理员账号！")
        data = r.body

        # if not
        try:
           json_data = json.loads(data.decode('utf8'))
        except Exception as e:
            logger.info('缺少参数.{}'.format(e))
            return to_json_data(errno=Code.PARAMERR,errmsg='缺少参数')
        form = NewsPubForm(json_data)
        if form.is_valid():
            news_instance = form.save(commit=False)
            news_instance.author = r.user
            news_instance.save()
            # print(r.user)
            return to_json_data(errmsg='文章发布成功')
        else:
            errno_msg_list = []
            for items in form.errors.get_json_data().values():
                errno_msg_list.append(items[0].get('message'))
            errno_list = ''.join(errno_msg_list)
            return to_json_data(errno=Code.PARAMERR,errmsg=errno_list)

class NewsEditView(PermissionRequiredMixin,View):
    permission_required = ('news.view_news', 'news.delete_news','news.change_news')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(NewsEditView, self).handle_no_permission()
    def get(self,r,news_id):
        try:
            news = News.objects.filter(id=news_id,is_delete=False).first()
        except Exception:
            return  to_json_data(errno=Code.PARAMERR,errmsg='无此数据')
        tags = Tag.objects.only('id', 'name').filter(is_delete=False)
        return render(r, 'admin/news/news_pub.html', locals())
    def put(self,r,news_id):
        data = r.body
        '''
        "title": sTitle,
        "digest": sDesc,
        "tag": sTagId,
        "image_url": sThumbnailUrl,
        "content": sContentHtml,
        '''
        try:
            news = News.objects.filter(id=news_id,is_delete=False).first()
        except Exception as e:

            return to_json_data(errno=Code.DBERR,errmsg='没有此新闻')
        try:
            json_data = json.loads(data.decode('utf8'))
            title = json_data.get('title').strip(' ')
            digest = json_data.get('digest').strip(' ')
            tag = int(json_data.get('tag'))
            image_url = json_data.get('image_url').strip(' ')
            content = json_data.get('content').strip(' ')
        except Exception as e:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        form = NewsPubForm(json_data)

        flg = news.title == title and news.digest == digest and news.tag_id == tag and \
              news.image_url == image_url and news.content == content
        if flg:
            return to_json_data(errno=Code.DATAEXIST,errmsg='数据未更改！')
        else:
            if form.is_valid():
                news.title = form.cleaned_data.get('title')
                news.digest = form.cleaned_data.get('digest')
                news.content = form.cleaned_data.get('content')
                news.image_url = form.cleaned_data.get('image_url')
                news.tag = form.cleaned_data.get('tag')
                news.save()
                return to_json_data(errmsg='文章更新成功')
            else:
                err_msg_list = []
                for items in form.errors.get_json_data().values():
                    err_msg_list.append(items[0].get('message'))
                err_list = "".join(err_msg_list)
                return to_json_data(errno=Code.PARAMERR,errmsg=err_list)

    def delete(self,r,news_id):
        try:
            news = News.objects.filter(id=news_id,is_delete=False).first()
        except Exception:
            return  to_json_data(errno=Code.PARAMERR,errmsg='无此数据')
        news.is_delete = True
        news.save(update_fields = ['update_time','is_delete'])
        return to_json_data(errmsg='删除成功')

class NewsUploadImage(View):

    def post(self,r):
        image_file = r.FILES.get('image_file')
        if not image_file:
            return  to_json_data(errno=Code.PARAMERR,errmsg='从前端获取图片失败')
        if image_file.content_type not in ('image/jpeg','image/png','image/gif'):
            return to_json_data(errno=Code.PARAMERR, errmsg='图片格式不正确')
        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.info("图片拓展名异常.{}".format(e))
            image_ext_name = 'jpg'
        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(),file_ext_name=image_ext_name)
        except Exception as e:
            logger.info('图片上传出现异常:{}'.format(e))
            return to_json_data(errno=Code.PARAMERR,errmsg='图片上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('图片上传到FastDFS服务器失败')
                return to_json_data(errno=Code.PARAMERR,errmsg='图片上传服务器异常')
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
                return to_json_data(data={'image_url':image_url})

class UpToken(View):
    def get(self,r):
        token = qiniu.Auth(QINIU_ACCESS_KEY,QINIU_SECRET_KEY).upload_token(QINIU_BUCKET_NAME)
        return JsonResponse({'uptoken':token})

from django.utils.decorators import method_decorator #这个是对类视图使用装饰器的方法
from django.views.decorators.csrf import csrf_exempt#取消单个视图csrf验证的装饰器
# @method_decorator(csrf_exempt,name='post')
@method_decorator(csrf_exempt,name='dispatch')
#由于所有请求方法都走dispatch('get','post'...) 无需只写一个请求方法 写一个dispatch就可以了
class MarkDownUpImageView(View):
    def post(self,r):
        image_file = r.FILES.get('editormd-image-file')
        if not image_file:
            logger.info('从前端获取图片失败')
            return JsonResponse({'success': 0, 'message': '从前端获取图片失败'})

        if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
            return JsonResponse({'success': 0, 'message': '不能上传非图片文件'})

        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.info('图片拓展名异常：{}'.format(e))
            image_ext_name = 'jpg'

        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传出现异常：{}'.format(e))
            return JsonResponse({'success': 0, 'message': '图片上传异常'})
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('图片上传到FastDFS服务器失败')
                return JsonResponse({'success': 0, 'message': '图片上传到服务器失败'})
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
                return JsonResponse({'success': 1, 'message': '图片上传成功', 'url': image_url})

class BannerEditView(PermissionRequiredMixin,View):
    '''
     "image_url"
      "priority"
      "banner_id"
    '''
    permission_required = ('banners.view_banners', 'banners.delete_banners','banner.change_banners')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(BannerEditView, self).handle_no_permission()
    def get(self,r):
        banners = Banner.objects.filter(is_delete=False)
        priority_dict = dict([ i for i  in Banner.PRI_CHOICE])
        # print(priority_dict)
        return render(r,'admin/news/news_banner.html',locals())
        # return JsonResponse({'priority_dict':[i for i in priority_dict]})
    def delete(self,r,banner_id):
        try:
            banners = Banner.objects.filter(is_delete=False,id=banner_id).first()

        except Exception as e:
            return to_json_data(errno=Code.NODATA,errmsg=error_map[Code.NODATA])
        banners.is_delete = True
        banners.save(update_fields = ['update_time','is_delete'])
        return to_json_data(errmsg='删除成功')
    def put(self,r,banner_id):
        data = r.body
        try:
            json_data = json.loads(data.decode('utf8'))
        except Exception:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        if not Banner.objects.filter(id=banner_id).first():
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        form = forms.BannersUpdateForm(json_data)
        if form.is_valid():
            banners = Banner.objects.filter(id=banner_id).first()
            banners.image_url = form.cleaned_data.get('image_url')
            banners.priority = form.cleaned_data.get('priority')
            banners.save()
            # print(banner_id)
            # print(form.cleaned_data.get('priority'))
            # print(form.cleaned_data.get('image_url'))
            return to_json_data(errmsg='更改成功！')

        else:
            err_msg = []
            for items in form.errors.get_json_data().values():
                err_msg.append(items[0].get('message'))
            err_msg_list = "".join(err_msg)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_list)

class BannerAddView(PermissionRequiredMixin,View):
    permission_required = ('banners.add_banners','banners.view_banners')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(BannerAddView, self).handle_no_permission()
    def get(self,r):
        tags = Tag.objects.filter(is_delete=False)

        priority_dict = dict([i for i in Banner.PRI_CHOICE])
        return render(r,'admin/news/news_banner_add.html',locals())
    def post(self,r):
        data = r.body
        try:
            json_data = json.loads(data.decode('utf8'))
            tag_id = int(json_data.get('tag_id'))
        except Exception :
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # print([i.id for i in Tag.objects.all()])
        if not (tag_id in [i.id for i in Tag.objects.filter(is_delete=False)]):
            return to_json_data(errno=Code.PARAMERR,errmsg='tag_id 错误')

        form = forms.BannersAddForm(data=json_data,tagid=tag_id)

        if form.is_valid():
            # banners = Banner.objects.first()
            # banners.image_url = form.cleaned_data.get('image_url')
            # banners.priority = form.cleaned_data.get('priority')
            # banners.news_id = form.cleaned_data.get('news_id')
            # banners.save()
            # print(form.changed_data)
            # print(form.cleaned_data.get('news_id'))
            banners_instance = form.save(commit=False)
            banners_instance.news_id = json_data.get('news_id')
            banners_instance.save()
            return to_json_data(errmsg='添加轮播图成功！')
        else:
            err_msg = []
            for items in form.errors.get_json_data().values():
                err_msg.append(items[0].get('message'))
            err_msg_list = "".join(err_msg)

            return to_json_data(errno=Code.PARAMERR,errmsg=err_msg_list)

class BannerOfNewsByTagView(View):
    def get(self,r,tag_id):
        banners = Banner.objects.only('news_id')
        banner_list = [i.news_id for i in banners]
        try:
            news = News.objects.filter(is_delete=False,tag_id=tag_id).values('id','title')
        except Exception :
            return to_json_data(errno=Code.NODATA,errmsg=error_map[Code.NODATA])
        news_list = [i['id'] for i in news]
        query_list = [ b for b in news_list if b not in banner_list ]
        news = news.filter(id__in=query_list)
        news = [i for i in news]
        return to_json_data(data={'news':news})


class DocsManageView(PermissionRequiredMixin,View):
    permission_required = ('docs.view_docs')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(DocsManageView, self).handle_no_permission()
    def get(self,r):
        docs =  Doc.objects.only('title','update_time').filter(is_delete=False)
        return render(r,'admin/doc/docs_manage.html',locals())

class DocsEditView(PermissionRequiredMixin,View):
    permission_required = ('docs.view_docs','dosc.delete_docs','docs.change_docs')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(DocsEditView, self).handle_no_permission()
    def get(self,r,doc_id):
        doc = Doc.objects.defer('author').filter(is_delete=False,id=doc_id).first()
        return render(r,'admin/doc/docs_pub.html',locals())
    def delete(self,r,doc_id):

        docs = Doc.objects.filter(is_delete=False,id=doc_id).first()
        if not docs:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.NODATA])
        docs.is_delete = True
        docs.save(update_fields=['is_delete','update_time'])
        return to_json_data(errmsg='删除成功')
    def put(self,r,doc_id):
        docs = Doc.objects.filter(is_delete=False, id=doc_id).first()
        if not docs:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.NODATA])
        data = r.body

        # if not
        try:
            json_data = json.loads(data.decode('utf8'))
        except Exception as e:
            logger.info('缺少参数.{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='缺少参数')

        form = forms.DocsPubForm(json_data)
        if form.is_valid():
            for attr,value in form.cleaned_data.items():
                setattr(docs,attr,value)
            docs.save()
            return to_json_data(errmsg='文档更新成功')
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

class DocsPubView(PermissionRequiredMixin,View):
    permission_required = ('docs.view_docs','docs.add_docs')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(DocsPubView, self).handle_no_permission()
    def get(self,r):
        return render(r,'admin/doc/docs_pub.html')
    def post(self,r):
        data = r.body

        try:
            json_data = json.loads(data.decode('utf8'))
        except Exception as e:
            logger.info('缺少参数.{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='缺少参数')
        form = DocsPubForm(json_data)
        if form.is_valid():
            docs_instance = form.save(commit=False)

            docs_instance.author = r.user
            docs_instance.save()
            return to_json_data(errmsg='文档创建成功')
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class DocsUploadFileView(View):
    """
    /admin/docs/files/
    """

    def post(self, request):
        text_file = request.FILES.get('text_file')
        if not text_file:
            logger.info('从前端获取文件失败!')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取文件失败')
        if text_file.content_type not in ('application/octet-stream', 'application/pdf',
                                          'application/zip', 'text/plain', 'application/x-rar'):
            return to_json_data(errno=Code.DATAERR, errmsg='只能上传文件')

        try:
            text_ext_name = text_file.name.split('.')[-1]
        except Exception as e:
            logger.info('文件拓展名异常：{}'.format(e))
            text_ext_name = 'pdf'

        try:
            upload_res = FDFS_Client.upload_by_buffer(text_file.read(), file_ext_name=text_ext_name)
        except Exception as e:
            logger.error('文件上传出现异常：{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='文件上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('文件上传到FastDFS服务器失败')
                return to_json_data(Code.UNKOWNERR, errmsg='文件上传到服务器失败')
            else:
                text_name = upload_res.get('Remote file_id')
                text_url = settings.FASTDFS_SERVER_DOMAIN + text_name
                return to_json_data(data={'text_file': text_url}, errmsg='文件上传成功')

class CoursesManageView(PermissionRequiredMixin,View):
    """
    /admin/courses/
    """
    permission_required = ('course.view_course')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(CoursesManageView, self).handle_no_permission()
    def get(self,request):
        courses = Course.objects.select_related('category','teacher').\
            only('title','category__name','teacher__name').filter(is_delete=False)
        return render(request,'admin/course/courses_manage.html',locals())

class CoursesEditView(PermissionRequiredMixin,View):
    """
    /admin/courses/<int:course_id>/
    """
    permission_required = ('course.view_course','course.change_course','course.delete_course')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(CoursesEditView, self).handle_no_permission()
    def get(self, request, course_id):
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if course:
            teachers = Teacher.objects.only('name').filter(is_delete=False)
            categories = CourseCategory.objects.only('name').filter(is_delete=False)
            return render(request, 'admin/course/courses_pub.html', locals())
        else:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的课程不存在')

    def delete(self, request, course_id):
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if course:
            course.is_delete = True
            course.save(update_fields=['is_delete','update_time'])
            return to_json_data(errmsg="课程删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的课程不存在")

    def put(self, request, course_id):
        course = Course.objects.filter(is_delete=False, id=course_id).first()
        if not course:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的课程不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        dict_data['online_play_url'] = dict_data['online_play_url'].replace(' ', '@')
        form = forms.CoursesPubForm(data=dict_data)
        if form.is_valid():
            for attr, value in form.cleaned_data.items():
                setattr(course, attr, value)

            course.save()
            return to_json_data(errmsg='课程更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

class CoursesPubView(PermissionRequiredMixin,View):
    """
    /admin/courses/pub/
    """
    permission_required = ('course.view_course','course.add_course')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(CoursesPubView, self).handle_no_permission()
    def get(self,request):
        teachers = Teacher.objects.only('name').filter(is_delete=False)
        categories = CourseCategory.objects.only('name').filter(is_delete=False)
        return render(request,'admin/course/courses_pub.html',locals())

    def post(self,request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        # print(dict_data['online_play_url'])
        dict_data['online_play_url'] = dict_data['online_play_url'].replace(' ','@')
        # print(dict_data['online_play_url'])
        # return to_json_data()
        form = forms.CoursesPubForm(data=dict_data)
        if form.is_valid():
            form.save()
            return to_json_data(errmsg='课程发布成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

class GroupManageView(PermissionRequiredMixin,View):
    permission_required = ('auth.view_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(GroupManageView, self).handle_no_permission()
    def get(self,r):
        groups = Group.objects.values('name','id').annotate(num_users=Count('user')).order_by('-num_users')
        return render(r,'admin/user/groups_manage.html',locals())


class GroupEditView(PermissionRequiredMixin,View):
    permission_required = ('auth.view_group','auth.delete_group','auth.change_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(GroupEditView, self).handle_no_permission()
    def get(self,r,group_id):
        group = Group.objects.filter(id=group_id).first()
        if not group:
            raise Http404('需要更新组不存在')
        group_users = [i.username for i in group.user_set.all()]
        users = Users.objects.filter(is_active=True)
        permissions = Permission.objects.only('id').all()
        return render(r, 'admin/user/groups_add.html', locals())
    def delete(self,r,group_id):
        group = Group.objects.filter(id=group_id).first()
        if group:
            # group.permissions.clear()#由于此表涉及多对多 不能直接删除 所以先清空权限
            # group.user_set.clear()
            group.delete()#由于group表是系统给的 没有is_delete 所以delete是真正的删除并且是级联删除 不需要以上两行代码
            return to_json_data(errmsg='用户组删除成功')
        else:
            return  to_json_data(errno=Code.PARAMERR,errmsg='需要删除的用户组不存在！')
    def put(self,r,group_id):
        group = Group.objects.filter(id=group_id).first()
        if  not group:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要编辑的用户组不存在！')
        data = r.body
        try:
            json_data = json.loads(data.decode('utf8'))
        except Exception as e:
            logger.info('错误：{}'.format(e))
            return to_json_data(errno=Code.PARAMERR,errmsg='参数缺失')

        users = json_data.get('group_users')
        initial_user = [ str(i.id) for i in group.user_set.filter(is_active=True)]
        if not Users.objects.filter(id__in=users):
            return to_json_data(errno=Code.PARAMERR,errmsg='含有不存在的用户')
        # print(Users.objects.filter(id__in=users))

        group_name = json_data.get('name','').strip(' ')
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')
        if group.name != group_name and (not Group.objects.filter(name=group_name).exists()):
            return to_json_data(errno=Code.PARAMERR, errmsg='组名已存在')
        group_permissions = json_data.get('group_permissions')
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')
        try:
            permissions_set = set(int(i) for i in group_permissions)
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数异常')
        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        if not permissions_set.issubset(all_permissions_set):#issubset判断前者set集合是否为后者set集合的字迹
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的权限参数')

        existed_permissions_set = set(i.id for i in group.permissions.all())
        if (not bool([i for i in users if i not in initial_user])) and \
                group_name == group.name and \
                permissions_set == existed_permissions_set:
            return to_json_data(errno=Code.DATAEXIST, errmsg='用户组信息未修改')
        # 设置权限
        group.permissions.clear()
        group.user_set.clear()
        u = Users.objects.filter(id__in=users)
        group.user_set.set(u)
        for perm_id in permissions_set:
            p = Permission.objects.get(id=perm_id)
            group.permissions.add(p.id)
        group.name = group_name
        group.save()
        return to_json_data(errmsg='组更新成功！')

class GroupsAddView(PermissionRequiredMixin,View):
    """
    /admin/groups/add/
    """
    permission_required = ('auth.view_group','auth.add_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(GroupsAddView, self).handle_no_permission()
    def get(self,request):
        permissions = Permission.objects.only('id').all()
        users = Users.objects.filter(is_active=True)
        return render(request,'admin/user/groups_add.html',locals())

    def post(self,request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        # 取出组名，进行判断
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')

        one_group, is_created = Group.objects.get_or_create(name=group_name)
        if not is_created:
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名已存在')

        # 取出权限
        group_permissions = dict_data.get('group_permissions')
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')

        try:
            permissions_set = set(int(i) for i in group_permissions)
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数异常')

        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        if not permissions_set.issubset(all_permissions_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的权限参数')
        users = dict_data.get('group_users')
        if not Users.objects.filter(id__in=users):
            return to_json_data(errno=Code.PARAMERR,errmsg='含有不存在的用户')
        u = Users.objects.filter(id__in=users)
        one_group.user_set.set(u)
        # 设置权限
        for perm_id in permissions_set:
            p = Permission.objects.get(id=perm_id)
            one_group.permissions.add(p)

        one_group.save()
        return to_json_data(errmsg='组创建成功！')

class UsersManageView(PermissionRequiredMixin,View):
    permission_required = ('user.view_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(UsersManageView, self).handle_no_permission()
    def get(self,r):
        users = Users.objects.only('username','is_staff','is_superuser').filter(is_active=True)
        # for i in users:
        #     print(i.groups.all())

        return render(r,'admin/user/users_manage.html',locals())


class UsersEditView(PermissionRequiredMixin,View):
    permission_required = ('users.view_users','users.change_users','users.delete_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg="您没有权限")
        else:
            return super(UsersEditView, self).handle_no_permission()
    def get(self,r,user_id):
        user_instance = Users.objects.filter(id=user_id,is_active=True).first()
        if user_instance:
            groups = Group.objects.all()
            return render(r,'admin/user/users_edit.html',locals())
        else:
            return Http404('此用户不存在')
    def delete(self,r,user_id):
        user_instance = Users.objects.filter(id=user_id, is_active=True).first()
        if user_instance:
            user_instance.groups.clear()
            user_instance.user_permissions.clear()
            user_instance.is_active = False
            user_instance.save()
            return to_json_data( errmsg='删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='用户不存在')
    def put(self,r,user_id):
        user_instance = Users.objects.filter(id=user_id, is_active=True).first()
        if not user_instance:
            return Http404('需要修改用户不存在')
        data = r.body
        try:
            json_data = json.loads(data.decode('utf8'))
            groups = json_data.get('groups')
            is_staff = json_data.get('is_staff')
            is_active = json_data.get('is_active')
            is_superuser = json_data.get('is_superuser')
            params = (is_staff,is_superuser,is_active)
            # print([ i for i in params ])
            if not all([int(i) in (1,0) for i in params ]):#如果列表里某个值不为True
                return to_json_data(errno=Code.PARAMERR,errmsg='参数错误')
        except Exception as e:
            logger.info('错误：{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数缺失')

        try:
            groups_set = set(int(i) for i in groups) if groups else set()
        except Exception as e:
            logger.info('传的用户组参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='用户组参数异常')

        all_groups_set = set(i.id for i in Group.objects.only('id'))
        if not groups_set.issubset(all_groups_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的用户组参数')

        gs = Group.objects.filter(id__in=groups_set)#从所有的组中 选出在新选择的组集合里的组
        # 先清除组
        user_instance.groups.clear()
        user_instance.groups.set(gs)#除了add 还可以用set add是单个添加实例对象 set是设置多个

        user_instance.is_staff = bool(is_staff)
        user_instance.is_superuser = bool(is_superuser)
        user_instance.is_active = bool(is_active)
        user_instance.save()
        return to_json_data(errmsg='用户信息更新成功！')


def test(r,name):
    tag = Tag.objects.filter(is_delete=False)
    print(name)
    return render(r,'admin/base/base2.html',locals())



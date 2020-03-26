from datetime import datetime
from urllib.parse import urlencode
from .forms import NewsPubForm
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse
import json
import logging
from django.http import FileResponse
import qiniu
from utils.qiniu_secret_info import *
from djproject import settings
from utils.fastdfs.fdfs import  FDFS_Client
from . import forms
from news.models import *
from utils.res_codes import *
from utils.json_fun import *
from django.views import View

from .constants import *
# Create your views here.
from .scripts import paginator_script

logger = logging.getLogger('django')
class IndexView(View):
    def get(self,r):
        return render(r,'admin/index/index.html')

class TagManagerView(View):
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

class TagEditView(View):
    '''
          url: "/admin/tags/" + sTagId + "/",
    '''
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

class HotNewsManagerView(View):
    def get(self,r):
        hot_news = HotNews.objects.select_related('news__tag').\
            only('news__title','news__tag__name','priority','news_id').\
            filter(is_delete=False).order_by('priority',"-update_time")[0:SHOW_HOSTNEWS_COUNT]
        # print(hot_news)
        return render(r,'admin/news/news_hot.html',locals())
class HotNewsEditView(View):
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


class HotNewsAddView(View):
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

class HotNewsGetView(View):
    def get(self,r,tag_id):

        tag_news = News.objects.select_related('tag').values('title','id').\
            filter(is_delete=False,tag_id=tag_id)
        news = [i for i in tag_news]

        return to_json_data(data={'news':news})


class NewsManageView(View):
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


class NewsPubView(View):
    '''
    /admin/news/pub/
    '''
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


class NewsEditView(View):
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


class BannerEditView(View):
    '''
     "image_url"
      "priority"
      "banner_id"
    '''
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



class BannerAddView(View):
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




def test(r,name):
    tag = Tag.objects.filter(is_delete=False)
    print(name)
    return render(r,'admin/base/base2.html',locals())




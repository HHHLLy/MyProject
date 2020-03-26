from django.shortcuts import render
from django.views import View

from djproject import settings
from news.models import *
from utils.json_fun import *
import logging
from utils.res_codes import *
from django.core.paginator import  Paginator,EmptyPage,PageNotAnInteger
from news.models import *
from news.constants import *
from django.http import Http404
import json
from haystack.views import SearchView as _SearchView

logger = logging.getLogger('django')
# Create your views here.




class IndexView(View):
    def get(self,r):
        # tags = Tag.objects.filter(is_delete=False)
        # context = {
        #     'tags':tags
        # }
        # return render(r,'news/index.html',context=context)

        # 优化
        # 当想把此函数里所有变量都传入可以用locals函数
        tags = Tag.objects.only('id','name').filter(is_delete=False)

        hotnews = HotNews.objects.select_related('news').only('news__title','news__image_url','news_id')\
            .filter(is_delete=False).order_by('priority','-update_time')[0:SHOW_HOSTNEWS_COUNT]
        return  render(r,'news/index.html',locals())

class NewsBannerView(View):
    def get(self,r):
        data_list = []
        banners = Banner.objects.select_related('news').only('image_url','news_id','news__title').\
            filter(is_delete=False).order_by('priority')[0:SHOW_BANNERS_COUNT]
        for i in banners:
            data_list.append({
                'image_url':i.image_url,
                'news_id':i.news.id,
                'news_title':i.news.title,
            })
        data = {
            'banners':data_list
        }
        return to_json_data(data=data)
        # return render(r,'news/news_detail.html',context={"banner":banners})

#news/?tag_id=1&page=1
class NewsListView(View):
    def get(self,r):
        #  1 获取和校验
        #当后台没拿到tag_id参数时 则设置此参数值默认为0 不能返回其他数据库可以查到的tag_id的值
        try:
            tag_id = int(r.GET.get('tag_id',0))
        except Exception as e:
            logger.error('标签参数错误:\n{}'.format(e))
            tag_id = 0
        try:
            page = int(r.GET.get('page',1))
        except Exception as e:
            logger.error('页码参数错误:\n{}'.format(e))
            page = 1
        #  2 数据库取数据
        # News表：title digest image_url update_time
        # author tag
        # 多表联合 select_related = select * from a,b where a.id = b.id
        # select_related 优化了访问数据库的次数
        # 下面的语句时 将news users tag 三表笛卡尔积联合起来 方便查询
        # id作为主键 可以不用写入 系统会自动查
        news_queryset = News.objects.select_related('tag','author').only('title','digest','image_url',
                                                         'update_time','tag__name','author__username',)
        #  当前面的news_queryset查询为None 则赋值后面的news_queryset查询给news也就是把最新更新的内容给news
        #  否则赋前面的
        news = news_queryset.filter(is_delete=False,tag_id=tag_id) or news_queryset.filter(is_delete=False)
        #  3 分页
        paginator = Paginator(news,PER_PAGE_NEWS_COUNT)#设置每页显示的数量
        try:
            news_info = paginator.page(page)
        except Exception as e:
            logger.error('用户访问页数超出总页数:\n{}'.format(e))
            news_info = paginator.page(paginator.num_pages)#返回最后一页
        news_info_list = []
        for n in news_info:
            news_info_list.append({
                'id':n.id,#如果用n_id是指这个queryset里id这个字段 而.是值
                'title': n.title,
                'digest': n.digest,
                'image_url': n.image_url,
                'tag_name': n.tag.name,
                'author': n.author.username,
                'update_time': n.update_time.strftime('%Y年%m月%d日 %H:%M'),
            })
        data = {
            'total_pages':paginator.num_pages,
            'news':news_info_list,
        }
        #  4 返回给前端
        return to_json_data(data=data)

class NewsDetailView(View):
    def get(self,r,news_id):
        news = News.objects.select_related('author','tag').\
        only('title','content','update_time','tag__name','author__username').\
        filter(is_delete=False,id=news_id).first()#加first 获得具体某个对像 不然就是queryset
        if news:
            #评论
            comments = Comments.objects.select_related('author','parent').only('content','author__username','update_time'
                                                                    ,'parent__content','parent__author__username',
                                                                    'parent__update_time').filter(is_delete=False,
                                                                                                  news_id=news_id)

            comments_list = []
            for comm in comments:
                comments_list.append(comm.to_dict_data())
            return render(r,'news/news_detail.html',locals())
        else:
            raise Http404('新闻{}不存在'.format(news_id))


class NewsCommentsView(View):
    '''
    /news/<int:news_id>/comments
    '''
    def post(self,r,news_id):
        if not r.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR,errmsg=error_map[Code.SESSIONERR])
        if not News.objects.filter(is_delete=False,id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR,errmsg="新闻不存在")
        data = r.body
        if not data:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        json_data = json.loads(data.decode('utf8'))
        content = json_data.get('content')
        if not content:
            return to_json_data(errno=Code.PARAMERR,errmsg="评论内容不能为空")
        parent_id = json_data.get('parent_id')
        try:
            # 如果传过来父评论id则查询是否有父评论id
            if parent_id:
                parent_id = int(parent_id)
                if not Comments.objects.only('id').filter(is_delete=False,id=parent_id,news_id=news_id).exists():
                    return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        except Exception as e:
            logger.info('parent_id异常{}'.format(e))
            return to_json_data(errno=Code.PARAMERR,error_map='未知异常')
        new_comment = Comments()
        new_comment.content = content
        new_comment.parent_id = parent_id if parent_id else None
        new_comment.author = r.user
        new_comment.news_id = news_id
        new_comment.save()
        return to_json_data(data=new_comment.to_dict_data())


class SearchView(_SearchView):
    # 模版文件
    template = 'news/search.html'

    # 重写响应方式，如果请求参数q为空，返回模型News的热门新闻数据，否则根据参数q搜索相关数据
    def create_response(self):
        kw = self.request.GET.get('q', '')
        if not kw:
            show_all = True
            hot_news = HotNews.objects.select_related('news'). \
                only('news__title', 'news__image_url', 'news__id'). \
                filter(is_delete=False).order_by('priority', '-news__clicks')

            paginator = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                page = paginator.page(int(self.request.GET.get('page', 1)))
            except PageNotAnInteger:
                # 如果参数page的数据类型不是整型，则返回第一页数据
                page = paginator.page(1)
            except EmptyPage:
                # 用户访问的页数大于实际页数，则返回最后一页的数据
                page = paginator.page(paginator.num_pages)
            return render(self.request, self.template, locals())
        else:
            show_all = False
            qs = super(SearchView, self).create_response()#在父类的create_respone会获取参数q
            return qs



        


















from common.func_modle import my_time
from django.shortcuts import render
from django.views import View
from datetime import datetime
from djproject import settings
from utils.json_fun import *
import logging
from utils.res_codes import *
from django.core.paginator import  Paginator,EmptyPage,PageNotAnInteger
from news.models import *
from news.constants import *
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from course.models import *

import json
from .weather_api import get_weather
from haystack.views import SearchView as _SearchView

logger = logging.getLogger('django')
# Create your views here.

class BaseHtmlView(View):
    def get(self,r):
        course = Course.objects.only('title','online_play_url').filter(is_delete=False,id=2).first()
        hotnews = HotNews.objects.select_related('news').only('news__image_url',
                                                              'news__title',
                                                              'news__update_time',
                                                              'news__tag__name',
                                                              'news__author__username',
                                                              'news_id').filter(is_delete=False).\
            order_by('-news__clicks')[0:SHOW_HOSTNEWS_COUNT]
        hotnews_list = []
        for i in hotnews:
            lt = {
                'image_url':i.news.image_url,
                'title':i.news.title,
                'update_time':i.news.update_time.strftime('%Y年%m月%d日'),
                'tag_name':i.news.tag.name,
                'author':i.news.author.username,
                'id':i.news.id
            }
            hotnews_list.append(lt)

        data = {
            'title':course.title,
            'video_url':course.online_play_url.replace('@',' '),
            'hotnews_list':hotnews_list
        }

        return to_json_data(data=data)

class BaseHtmlWeather(View):
    def get(self,r):
        weather_content = []
        initial_content = get_weather('长春')
        content = initial_content.get('result')
        for i in content.get('daily'):
            dit = {
                "date": int(i.get('date').split('-')[-1]),
                "week": i.get('week'),
                "templow": i.get('night').get('templow'),
                "weather": i.get('day').get('weather'),
                "temp": i.get('day').get('temp'),
                "temphigh": i.get('day').get('temphigh'),
                "img": str(i.get('day').get('img')),
                "winddirect": i.get('day').get('winddirect'),
                "windpower": i.get('day').get('windpower')
            }
            weather_content.append(dit)
        weather_content = weather_content[:7]
        today_weater = weather_content.pop(0)
        city = content.get('city')
        updatetime = ":".join(content.get('updatetime').split(' ')[-1].split(':')[-3:-1])
        return to_json_data(errno=Code.OK, data={"today_weather": today_weater,
                                                 "city": city,
                                                 "updatetime": updatetime,
                                                 "weather_list": weather_content})
    def post(self,r):
        data = r.body
        json_data = json.loads(data.decode('utf8'))
        if not json_data:
            return to_json_data(errno=Code.PARAMERR,errmsg='内容为空')
        try:
            city = str(json_data.get('city'))
        except Exception :
            return to_json_data(errno=Code.PARAMERR,errmsg='参数不存在')
        try:
            flg = get_weather(city)
        except Exception as e:
            return to_json_data(errno=Code.PARAMERR,errmsg='')
        if flg.get('status') != 0:
            return to_json_data(errno=Code.PARAMERR, errmsg=flg.get('msg'))
        weather_content = []
        initial_content = flg
        content = initial_content.get('result')
        for i in content.get('daily'):
            dit = {
                "date": int(i.get('date').split('-')[-1]),
                "week": i.get('week'),
                "templow": i.get('night').get('templow'),
                "weather": i.get('day').get('weather'),
                "temp": i.get('day').get('temp'),
                "temphigh": i.get('day').get('temphigh'),
                "img": str(i.get('day').get('img')),
                "winddirect": i.get('day').get('winddirect'),
                "windpower": i.get('day').get('windpower')
            }
            weather_content.append(dit)
        weather_content = weather_content[:7]
        today_weater = weather_content.pop(0)
        city = content.get('city')
        updatetime = ":".join(content.get('updatetime').split(' ')[-1].split(':')[-3:-1])
        return to_json_data(errno=Code.OK, data={"today_weather": today_weater,
                                                 "city": city,
                                                 "updatetime": updatetime,
                                                 "weather_list": weather_content})
def baseHtmlweather(r):
    weather_content = []
    initial_content = get_weather('长春')
    content = initial_content.get('result')
    for i in content.get('daily'):
        dit = {
            "date":int(i.get('date').split('-')[-1]),
            "week":i.get('week'),
            "templow":i.get('night').get('templow'),
            "weather":i.get('day').get('weather'),
            "temp":i.get('day').get('temp'),
            "temphigh":i.get('day').get('temphigh'),
            "img":str(i.get('day').get('img')),
            "winddirect":i.get('day').get('winddirect'),
            "windpower":i.get('day').get('windpower')
        }
        weather_content.append(dit)
    weather_content = weather_content[:7]
    today_weater = weather_content.pop(0)
    city = content.get('city')
    updatetime  = ":".join(content.get('updatetime').split(' ')[-1].split(':')[-3:-1])
    return to_json_data(errno=Code.OK,data={"today_weather":today_weater,
                                            "city":city,
                                            "updatetime":updatetime,
                                            "weather_list":weather_content})

class IndexView(View):
    @method_decorator(cache_page(300))
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
            return Http404('新闻{}不存在'.format(news_id))


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
        count = Comments.objects.filter(is_delete=False, news_id=news_id).count()


        strf_datetime = datetime.strftime(new_comment.update_time,'%Y-%m-%d %H:%M')

        rst_time = my_time(strf_datetime)


        return to_json_data(data={'news_comment':new_comment.to_dict_data(),'ccount':count,
                                  'time':rst_time})

class NewsCommentsDelView(View):
    def get(self,r,news_id,comment_id):
        try:
            comment = Comments.objects.filter(id=comment_id,is_delete=False).first()
        except Exception:
            return to_json_data(errno=Code.PARAMERR,errmsg='没有此评论')
        comment.is_delete = True
        comment.save(update_fields=['is_delete','update_time'])
        count = Comments.objects.filter(is_delete=False, news_id=news_id).count()
        return to_json_data(errmsg='删除成功',data={'ccount':count})

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



        


















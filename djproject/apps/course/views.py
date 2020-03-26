from django.shortcuts import render
from django.views import View
from .models import *
from django.http import Http404
import logging
# Create your views here.
logger = logging.getLogger('django')
def course_list(r):
    course = Course.objects.select_related('teacher').only('title','teacher__name','teacher__avatar_url','cover_url')\
        .filter(is_delete=False)
    return render(r,'course/course.html',locals())
class Course_detail(View):
    def get(self,r,course_id):
        try:
            course = Course.objects.select_related('teacher').only('teacher__name','video_url','title','cover_url',
                                                                   'teacher__avatar_url',
                                'teacher__positional_title','teacher__profile','profile','outline')\
                                                                   .filter(is_delete=False,id=course_id).first()
            return render(r,'course/course_detail.html',locals())
        except Exception as e:
            logger.info('视频播放出错.{}'.format(e))
            raise Http404('页面不存在')


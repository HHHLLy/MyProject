from django.shortcuts import render,redirect,reverse
from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from utils.QQ_login import *
# Create your views here.
from django.http import HttpResponse
from utils.json_fun import *
class QQAuthView(View):

    def get(self,r):
        try:
            state = r.META['HTTP_REFERER']
        except Exception as e:
            state = 'http://127.0.0.1:9000/users/login/'
        auth = OAuthQQ(client_id=app_id, client_secret=ak, redirect_uri=red_url, state="")
        login_url = auth.get_qq_url()
        print(login_url)

        return to_json_data(data={'login_url':login_url})
def demo(r):
    a = 1
    aa = 2
    
    return HttpResponse('Successful!')
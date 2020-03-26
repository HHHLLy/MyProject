from django.shortcuts import render,redirect,reverse
from django.views import View
from utils.json_fun import to_json_data
from utils.res_codes import *
from django.contrib.auth import logout,login
import json
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from users.forms import RegisterForm,LoginForm,ResetForm
from users.models import Users
# Create your views here.
class RegisterView(View):
    '''
    /register/
    '''

    def get(self,r):
       return render(r,"users/register.html")
    def post(self,r):
        json_data = r.body
        if not json_data:
            return to_json_data(error=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        form = RegisterForm(data=json.loads(json_data.decode('utf8')))
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            user = Users.objects.create_user(username=username,password=password,mobile=mobile)
            # user.save()
            login(r,user)#保存登录信息给session
            return to_json_data(errmsg="注册成功！")
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = ''.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR,errmsg=err_msg_str)




class LoginView(View):
    # @method_decorator(ensure_csrf_cookie)
    def get(self,r):
        return  render(r,"users/login.html")
    def post(self,r):
        data = r.body
        if not data:
            return  to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        json_data = json.loads(data.decode('utf8'))
        form = LoginForm(data=json_data,request=r)
        if form.is_valid():

            return to_json_data(errno=Code.OK)
        else:
            error_msg_list = []
            for items in form.errors.get_json_data().values():
                error_msg_list.append(items[0].get('message'))
            errlist = "".join(error_msg_list)
            return to_json_data(errno=Code.PARAMERR,errmsg=errlist)



class LogoutView(View):
    def get(self,r):
        logout(r)
        return redirect(reverse("login"))




class ResetPwdView(View):
    def get(self,r):
        return render(r,'users/resetpwd.html')
    def post(self,r):
       data =  r.body
       if not data:
           return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
       json_data = json.loads(data.decode('utf8'))
       form = ResetForm(json_data)
       if form.is_valid():
           return to_json_data()
       else:
           err_msg_list = []
           for items in form.errors.get_json_data().values():
               err_msg_list.append(items[0].get('message'))

           err_list = "".join(err_msg_list)
           return to_json_data(errno=Code.PARAMERR, errmsg=err_list)

def up(r):
    user = Users.objects.filter(mobile=13111111111).first()
    # user.password = 'qwe123'
    # user.save()
    return HttpResponse(user.username)
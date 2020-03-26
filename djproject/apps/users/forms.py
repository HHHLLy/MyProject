import re
from django_redis import get_redis_connection
from django import forms
from django_redis import get_redis_connection
from users.models import Users
from verifications.contants import SMS_CODE_NUMS
from .models import Users
from django.db.models import Q
from django.contrib.auth import login

from users.constants import USER_SESSION_EXPIRE
class RegisterForm(forms.Form):

    """
    """
    username = forms.CharField(label='用户名', max_length=20, min_length=5,
                               error_messages={"min_length": "用户名长度要大于5", "max_length": "用户名长度要小于20",
                                               "required": "用户名不能为空"}
                               )
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=SMS_CODE_NUMS, min_length=SMS_CODE_NUMS,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})
    # 除了像在校验app里的form表单中mobile字段实行校验器的方法外，还可以像现在这样单独检验一个字段
    def clean_mobile(self):
        """

        """
        tel = self.cleaned_data.get('mobile')
        if not re.match(r"^1[3-9]\d{9}$", tel):
            raise forms.ValidationError("手机号码格式不正确")

        if Users.objects.filter(mobile=tel).exists():
            raise forms.ValidationError("手机号已注册，请重新输入！")

        return tel
    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data.get('mobile')
        pwd = cleaned_data.get('password')
        pwd_rpt = cleaned_data.get('password_repeat')
        usrn = cleaned_data.get('username')
        sms_text = cleaned_data.get('sms_code')
        if pwd != pwd_rpt:
            raise forms.ValidationError('两次密码不一致')
        if Users.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('手机号已注册')
        if Users.objects.filter(username=usrn).exists():
            raise  forms.ValidationError("用户名已存在")
        sms_fmt = 'sms_{}'.format(mobile)
        con = get_redis_connection(alias='verify_codes')
        sms_real_ansr = con.get(sms_fmt)
        if (not sms_real_ansr) or sms_text != sms_real_ansr.decode():
            raise  forms.ValidationError('短信验证码错误')




class LoginForm(forms.Form):
    user_account = forms.CharField()
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"})
    remember_me = forms.BooleanField(required=False)
    def __init__(self,*args,**kwargs):
        #由于在表单里验证记住我勾选框 login需要一个request参数 则需要继承重写父类form的init方法
        #添加个request参数 这样在view视图里调用时就可以把request传进来
        self.request = kwargs.pop('request',None)#pop方法：弹出键值对。拿到键值对后删除键值对
        super().__init__(*args,**kwargs)

    def clean_user_account(self):
        user_info = self.cleaned_data.get('user_account')
        if not user_info:
            raise forms.ValidationError('用户名不能为空！')
        if not re.match(r'^1[3-9]\d{9}$',user_info) and (len(str(user_info))<5 or len(str(user_info))>20):
            raise forms.ValidationError('账号格式不正确')
        return user_info
    def clean(self):
        clean_data = super().clean()
        user_info = clean_data.get('user_account')
        pwd = clean_data.get('password')
        hold_login = clean_data.get('remember_me')
        user_queryset = Users.objects.filter(Q(username=user_info) | Q(mobile=user_info))
        if user_queryset:
            user = user_queryset.first()
            if user.check_password(pwd):#由于数据库的密码是加密的不能直接和前端拿来的密码比较 所以用到了check_password方法来比较
                if not hold_login:
                    self.request.session.set_expiry(0)
                    # 如果没勾选remember_me 则设置session过期时间为None也就是立刻过期删除session
                else:
                    self.request.session.set_expiry(USER_SESSION_EXPIRE)
                login(self.request,user)
            else:
                raise forms.ValidationError('密码错误！')
        else:
            raise forms.ValidationError('账号不存在！')


class ResetForm(forms.Form):

    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )

    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=SMS_CODE_NUMS, min_length=SMS_CODE_NUMS,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not re.match(r"^1[3,9]\d{9}$",mobile):
            raise forms.ValidationError('手机号格式不正确')
        return mobile
    def clean(self):
        clean_data = super().clean()
        mobile = clean_data.get('mobile')
        pwd = clean_data.get('password')
        sms = clean_data.get('sms_code')
        con = get_redis_connection(alias='verify_codes')
        sms_fmt = 'sms_{}'.format(mobile)
        redis_sms_code = con.get(sms_fmt)
        if redis_sms_code.decode() == sms :
            if  Users.objects.filter(mobile=mobile).first().password != pwd:
                user = Users.objects.filter(mobile=mobile).first()
                user.set_password(pwd)
                user.save()
            else:
                raise  forms.ValidationError('密码不能与上次相同！')
        else:
            raise forms.ValidationError('信息验证码错误')





from django.shortcuts import render
import logging
import json
import re
from django.db.models import Q
import random
import string
from utils.captcha.captcha import captcha
from django.http import HttpResponse,JsonResponse
from django_redis import get_redis_connection
from django.views import View
from utils.yuntongxun.sms import CCP
from .contants import IMG_CODE_REDIS_EXPIRES,SMS_CODE_NUMS,SEND_SMS_CODE_INTERVAL,SMS_CODE_TEMP_ID,SMS_CODE_REDIS_EXPIRES
from users import models
from utils.res_codes import Code,error_map
from utils.json_fun import to_json_data
from .forms import CheckImageCodeForm,CheckResetForm
from users.models import Users
# Create your views here.
logger = logging.getLogger("django")
class ImageView(View):
    def get(self,request,image_code_id):
        text ,image = captcha.generate_captcha()
        con_redis = get_redis_connection(alias='verify_codes')#指定存放在那个redis数据库中
        img_key = "img_{}".format(image_code_id)
        con_redis.setex(img_key,IMG_CODE_REDIS_EXPIRES,text)#建立键值对 过期时间300s
        logger.info("IMG_INFO: {}".format(text))
        return HttpResponse(content=image,content_type="image/png")

class CheckUsernameView(View):
    def get(self,r,username):
        count = models.Users.objects.filter(username=username).count()
        data = {
            "count":count,
            "username":username
        }

        # return JsonResponse({"data":data})
        return to_json_data(data=data)
class CheckMobileView(View):
    def get(self,r,mobile):
        count = models.Users.objects.filter(mobile=mobile).count()
        data = {
            "count": count,
            "mobile": mobile
        }
        # return JsonResponse({"data": data})
        return to_json_data(data=data)


#手机： 不为空。格式正确。手机未被注册
#验证码：不为空。与数据库存入的值相同
#uuid：格式正确

class CheckResetUserView(View):
    def get(self,r,reset_mobile):
        if re.match('^1[3-9]\d{9}$',reset_mobile):
            count = Users.objects.filter(mobile=reset_mobile).count()
        else:
            count = Users.objects.filter(username=reset_mobile).count()
        return to_json_data(data={'mobile':reset_mobile,'count':count})

class CheckResetPwdView(View):
    def get(self,r):
        try:
            mobile = r.GET.get('mobile',"")
            pwd = r.GET.get('pwd',"")
        except Exception as e:
            return to_json_data(errno=Code.NODATA, errmsg="无数据")
        if not( re.match('^1[3,9]\d{9}$',mobile) and re.match('\d{5}',pwd) ):
            return to_json_data(errno=Code.PARAMERR, errmsg="手机号或密码格式不正确")
        if not (mobile and pwd):
            return to_json_data(errno=Code.PARAMERR, errmsg="需要同时输入手机和密码")
        try:


            user = Users.objects.filter(Q(username=mobile)|Q(mobile=mobile)).first()


            if  user.check_password(pwd):
                return to_json_data(errno=Code.NODATA, errmsg="密码不能与上次相同！")
            return to_json_data(errmsg='密码可用！')
        except Exception as e:
            logger.info("密码更改异常.{}".format(e))
            return to_json_data(errno=Code.NODATA,errmsg='没有此用户！')




class SmsCodesView(View):

#     /sms_codes/

    def post(self,r):
        # 因为是post所以通过body拿到传过来的值
        json_data = r.body
        print("body：    "+str(json_data))
        if not json_data:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode("utf8"))
        # 验证参数
        form = CheckImageCodeForm(data=dict_data)

        if form.is_valid():
            #发送短信
            mobile = form.cleaned_data.get('mobile')

            # sms_num = ''
            # for i in range(6):
            #     random.choice(string.digits)#string.digits是从零至九的数字的字符串
            sms_num = "".join([random.choice(string.digits) for i in range(SMS_CODE_NUMS)])
            # 保存短信验证码
            con_redis = get_redis_connection(alias="verify_codes")
            pl = con_redis.pipeline()
            sms_text_fmt = "sms_{}".format(mobile)# 验证码的键
            sms_flag_fmt = "sms_flag_{}".format(mobile)# 发送标记
            # 检测发送信息是否在上一次发送的60s后
            sms_flg = con_redis.get(sms_flag_fmt)

            if sms_flg:
                return to_json_data(errno=Code.SMSRATEFALL,errmsg=error_map[Code.SMSRATEFALL])
            try:
                pl.setex(sms_flag_fmt,SEND_SMS_CODE_INTERVAL,SMS_CODE_TEMP_ID)
                pl.setex(sms_text_fmt,SMS_CODE_REDIS_EXPIRES,sms_num)
                pl.execute()
            except Exception as e:
                logger.debug("redis 执行异常: {}".format(e))
                return to_json_data(errno=Code.UNKOWNERR,errmsg=error_map[Code.UNKOWNERR])
        # 发送短信验证码
        # 为了节省资源 将跳过调用云通讯短信而直接发送成功

        #     logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
        #     return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
        # else:
        #     # 定义一个错误信息列表 也就是form里raise出的错误
        #     err_msg_list = []
        #     for item in form.errors.get_json_data().values():
        #         err_msg_list.append(item[0].get('message'))
        #         # print(item[0].get('message'))   # for test
        #     err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
        #
        #     return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)
            try:
                result = CCP().send_template_sms(mobile,
                                                 [sms_num, SMS_CODE_REDIS_EXPIRES],
                                                 SMS_CODE_TEMP_ID)
            except Exception as e:
                logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
                return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            else:
                if result == 0:
                    logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
                    return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
                else:
                    logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
                    return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class ResetSmsCodesView(View):

#     /sms_codes/

    def post(self,r):
        # 因为是post所以通过body拿到传过来的值
        json_data = r.body
        print("body：    "+str(json_data))
        if not json_data:
            return to_json_data(errno=Code.PARAMERR,errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode("utf8"))
        # 验证参数
        form = CheckResetForm(data=dict_data)

        if form.is_valid():
            #发送短信
            mobile = form.cleaned_data.get('mobile')

            # sms_num = ''
            # for i in range(6):
            #     random.choice(string.digits)#string.digits是从零至九的数字的字符串
            sms_num = "".join([random.choice(string.digits) for i in range(SMS_CODE_NUMS)])
            # 保存短信验证码
            con_redis = get_redis_connection(alias="verify_codes")
            pl = con_redis.pipeline()
            sms_text_fmt = "sms_{}".format(mobile)# 验证码的键
            sms_flag_fmt = "sms_flag_{}".format(mobile)# 发送标记
            # 检测发送信息是否在上一次发送的60s后
            sms_flg = con_redis.get(sms_flag_fmt)

            if sms_flg:
                return to_json_data(errno=Code.SMSRATEFALL,errmsg=error_map[Code.SMSRATEFALL])
            try:
                pl.setex(sms_flag_fmt,SEND_SMS_CODE_INTERVAL,SMS_CODE_TEMP_ID)
                pl.setex(sms_text_fmt,SMS_CODE_REDIS_EXPIRES,sms_num)
                pl.execute()
            except Exception as e:
                logger.debug("redis 执行异常: {}".format(e))
                return to_json_data(errno=Code.UNKOWNERR,errmsg=error_map[Code.UNKOWNERR])
        # 发送短信验证码
        # 为了节省资源 将跳过调用云通讯短信而直接发送成功

            logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
        else:
            # 定义一个错误信息列表 也就是form里raise出的错误
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)
        #     try:
        #         result = CCP().send_template_sms(mobile,
        #                                          [sms_num, SMS_CODE_REDIS_EXPIRES],
        #                                          SMS_CODE_TEMP_ID)
        #     except Exception as e:
        #         logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
        #         return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
        #     else:
        #         if result == 0:
        #             logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
        #             return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
        #         else:
        #             logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
        #             return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
        # else:
        #     # 定义一个错误信息列表
        #     err_msg_list = []
        #     for item in form.errors.get_json_data().values():
        #         err_msg_list.append(item[0].get('message'))
        #         # print(item[0].get('message'))   # for test
        #     err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
        #
        #     return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)



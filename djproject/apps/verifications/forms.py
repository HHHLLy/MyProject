#为什么用到forms表单？
# 在views视图里 出现多层验证时 不能用if
#  此时用django的forms验证功能 clean函数上面的代码时检查输入的格式 下面的时检验是否与数据库内容相同
from django import forms
from django.core.validators import RegexValidator#正则校验器
from users.models import Users

from django_redis import get_redis_connection
mobile_validator = RegexValidator(r"1[3-9]\d{9}$","手机号码格式不正确")
class CheckImageCodeForm(forms.Form):
    '''
    字段名得和js传过来的参数名一致 也就是和前端页面字段id值一致
    '''
    mobile = forms.CharField(max_length=11,min_length=11,validators=[mobile_validator,],
    error_messages={"min_length":"手机长度有误", "max_length": "手机号长度有误","required": "手机号不能为空"})
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    text = forms.CharField(max_length=4, min_length=4,
                           error_messages={"min_length": "图片验证码长度有误", "max_length": "图片验证码长度有误",
                                        "required": "图片验证码不能为空"})
    def clean(self):
        # 固定写法
        # 如果是单独检验某字段 则此函数命名为clean_加上面的字段名
        # 如果是检验所有字段 命名则为clean
        data_clean = super().clean()
        # 进行cleaned_data 重写
        # 由于数据都存在data_clean里 所以用get取到值

        mobile_num = data_clean.get('mobile')
        image_text = data_clean.get('text')  #用户输入的图形验证码
        image_uuid = data_clean.get('image_code_id')
        if Users.objects.filter(mobile=mobile_num):
            raise forms.ValidationError("手机号已被注册")
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_uuid)
        real_image_code_origin = con_redis.get(img_key)#取出来的是bytes类型
        if real_image_code_origin:
            real_image_code_origin = real_image_code_origin.decode("utf8")
        else:
            real_image_code_origin =  None
        # real_image_code_origin = real_image_code_origin.decode("urf8") if real_image_code_origin else None
        # con_redis.delete(img_key)#取出后将其删掉
        if (not real_image_code_origin) or (real_image_code_origin != image_text.upper()):
            raise forms.ValidationError("图形验证失败")
            # 检测发送信息是否在上一次发送的60s后
        # sms_flag_fmt = "sms_flag_{}".format(mobile_num)
        # sms_flg = con_redis.get(sms_flag_fmt)
        # if sms_flg:
        #    raise forms.ValidationError('短信发送过快')


class CheckResetForm(forms.Form):
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={"min_length": "手机长度有误", "max_length": "手机号长度有误", "required": "手机号不能为空"})
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    text = forms.CharField(max_length=4, min_length=4,
                           error_messages={"min_length": "图片验证码长度有误", "max_length": "图片验证码长度有误",
                                           "required": "图片验证码不能为空"})

    def clean(self):
        # 固定写法
        # 如果是单独检验某字段 则此函数命名为clean_加上面的字段名
        # 如果是检验所有字段 命名则为clean
        data_clean = super().clean()
        # 进行cleaned_data 重写
        # 由于数据都存在data_clean里 所以用get取到值

        mobile_num = data_clean.get('mobile')
        image_text = data_clean.get('text')  # 用户输入的图形验证码
        image_uuid = data_clean.get('image_code_id')
        if not Users.objects.filter(mobile=mobile_num):
            raise forms.ValidationError("手机号未被被注册")
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_uuid)
        real_image_code_origin = con_redis.get(img_key)  # 取出来的是bytes类型
        if real_image_code_origin:
            real_image_code_origin = real_image_code_origin.decode("utf8")
        else:
            real_image_code_origin = None
        # real_image_code_origin = real_image_code_origin.decode("urf8") if real_image_code_origin else None
        # con_redis.delete(img_key)#取出后将其删掉
        if (not real_image_code_origin) or (real_image_code_origin != image_text.upper()):
            raise forms.ValidationError("图形验证失败")
            # 检测发送信息是否在上一次发送的60s后
        # sms_flag_fmt = "sms_flag_{}".format(mobile_num)
        # sms_flg = con_redis.get(sms_flag_fmt)
        # if sms_flg:
        #    raise forms.ValidationError('短信发送过快')




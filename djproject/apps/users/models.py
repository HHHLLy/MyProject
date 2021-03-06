from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager as _UserManager
# Create your models here.
class UserManager(_UserManager):
    def create_superuser(self, username, password, email=None, **extra_fields):
        super(UserManager,self).create_superuser(username=username,email=email,password=password,**extra_fields)


class Users(AbstractUser):
    objects = UserManager()#因为要继承重写 所以AbstractUser源码里objects成员属性的值要改成自己重写的UserManage()
    #此objects作用是 在视图里调用模型方法都是模型对象.objects.方法 objects就是作用于此
    REQUIRED_FIELDS = ['mobile']#重写create_superuser后将根据需求添加mobile字段则在这里添加
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号",help_text="手机号",
                              error_messages={"unique":'此手机号已被注册'})
    email_active = models.BooleanField(default=False,verbose_name="邮箱验证状态")
    class Meta:
        db_table = "tb_users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.username
    def get_groups_name(self):
        return "|".join([i.name for i in self.groups.all()])


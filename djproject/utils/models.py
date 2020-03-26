from django.db import models
import pytz
class ModelBase(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="修改时间")
    is_delete = models.BooleanField(default=False,verbose_name="逻辑删除")
    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     if  type(self.update_time):
    #         self.update_time = self.local_update_time()
    class Meta:
        abstract = True
        #设置为抽象类 这样数据库迁移时就不会专门生成这个类的表 而只用来被继承
    # def local_update_time(self):
    #     shanghai_timezone = pytz.timezone('Asia/Shanghai')
    #     local_update_time = shanghai_timezone.normalize(self.update_time)
    #     return local_update_time


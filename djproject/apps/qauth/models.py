from django.db import models
from utils.models import *

# Create your models here.
class QQAuth(ModelBase):
    user = models.OneToOneField('users.Users',on_delete=models.CASCADE)
    openid = models.CharField(max_length=64,verbose_name='openid')
    class Meta:
        db_table = 'tb_qq'
        verbose_name = 'QQ绑定用户'
        verbose_name_plural = verbose_name


from django.core.validators import MinLengthValidator
from django.db import models
import pytz
from utils.models import ModelBase
# Create your models here.
class Tag(ModelBase):
    name = models.CharField(max_length=64, verbose_name="标签名", help_text="标签名")

    class Meta:
        ordering = ['-update_time', '-id']
        #ordering作用于表内字段的排序 改变哪个字段就写入哪个字段 默认时升序排列 加负号就是降序
        db_table = "tb_tag"  # 指明数据库表名
        verbose_name = "新闻标签"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.name


class News(ModelBase):
    title = models.CharField(validators=[MinLengthValidator(1)],max_length=150,verbose_name="标题",help_text='标题')
    digest = models.CharField(max_length=200,verbose_name='摘要',help_text='摘要')
    content = models.TextField(verbose_name='内容',help_text='内容')
    clicks = models.IntegerField(default=0,verbose_name='点击量',help_text='点击量')
    image_url = models.URLField(default='',verbose_name='图片url',help_text='图片url')
    tag = models.ForeignKey('Tag',on_delete=models.SET_NULL,null=True)
    #ForeignKey 外键 也是一对多 通常设置一对多 时都设置在'多'的一方
    #级联删除
    # on_delete=CASCADE 删除关联数据时 与其关联自动删除
    # SET_NULL 删除关联数据时 与其关联的数据设为null null=True 可以为空
    author = models.ForeignKey('users.Users',on_delete=models.SET_NULL,null=True)
    class Meta:
        ordering = ['-update_time','-id']
        db_table = 'tb_news' #指明数据库表名
        verbose_name = '新闻' #在admin站点中显示的表名
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.title


class Comments(ModelBase):
    content = models.TextField(verbose_name='内容',help_text='内容')
    author =  models.ForeignKey('users.Users',on_delete=models.SET_NULL,null=True)
    news = models.ForeignKey('News',on_delete=models.CASCADE)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    #parent字段作用是允许评论别人的评论 所以关联自己
    #可以为空是因为没有父评论的话直接单独一个评论
    # 模型里序列化
    def to_dict_data(self):
        # shanghai_timezone = pytz.timezone('Asia/Shanghai')
        # local_update_time = shanghai_timezone.normalize(self.update_time)
        comment_data = {
            'news_id':self.news.id,
            'content_id':self.id,
            'content':self.content,
            'author':self.author.username,
            'update_time':self.update_time.strftime('%Y年%m月%d日 %H:%M'),
            'parent':self.parent.to_dict_data() if self.parent else None,
        }
        return comment_data
    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_comments"  # 指明数据库表名
        verbose_name = "评论"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<评论{}>'.format(self.id)


class HotNews(ModelBase):
    PRI_CHOICE=[
        (1,'第一级'),
        (2,'第二级'),
        (3,'第三级'),
    ]
    news = models.OneToOneField("News",on_delete=models.CASCADE)
    priority = models.IntegerField(choices=PRI_CHOICE,default=3,verbose_name='优先级',help_text='优先级')
    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_hotnews"  # 指明数据库表名
        verbose_name = "热门新闻"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<热门新闻{}>'.format(self.id)


class Banner(ModelBase):
    PRI_CHOICE=[
        (1,'第一级'),
        (2,'第二级'),
        (3,'第三级'),
        (4,'第四级'),
        (5,'第五级'),
        (6,'第六级'),
    ]
    image_url = models.URLField(verbose_name="轮播图url", help_text="轮播图url")
    priority = models.IntegerField(choices=PRI_CHOICE,default=6,verbose_name="优先级", help_text="优先级")
    news = models.OneToOneField('News', on_delete=models.CASCADE)

    class Meta:
        ordering = ['priority', '-update_time', '-id']
        db_table = "tb_banner"  # 指明数据库表名
        verbose_name = "轮播图"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<轮播图{}>'.format(self.id)




from django import forms
from news.models import *
from news.models import News, Tag
class TagEditForm(forms.Form):
    name = forms.CharField(min_length=1,max_length=10,error_messages={"min_length": "用户名长度要大于5",
                                                                   "max_length": "用户名长度要小于20",})
    def __init__(self,*args,**kwargs):
        self.tag_id = kwargs.pop('tag_id','')
        super().__init__(*args,**kwargs)
    def clean(self):
        clean_data = super().clean()

        name = clean_data.get('name').strip(' ')
        flag = Tag.objects.filter(name=name,is_delete=False).exists()
        if flag:
            raise forms.ValidationError('标签名称重复！！')
        else:
            tag = Tag.objects.filter(id=self.tag_id,is_delete=False).first()
            tag.name = name
            tag.save(update_fields=['name'])



class NewsPubForm(forms.ModelForm):
    """
    """
    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})
    tag = forms.ModelChoiceField(queryset=Tag.objects.only('id').filter(is_delete=False),
                                 error_messages={"required": "文章标签id不能为空", "invalid_choice": "文章标签id不存在", }
                                 )
    class Meta:
        model = News  # 与数据库模型关联
        # 需要关联的字段
        # exclude = []排除
        fields = ['title', 'digest', 'content', 'image_url', 'tag']
        error_messages = {
            'title': {
                'max_length': "文章标题长度不能超过150",
                'min_length': "文章标题长度大于1",
                'required': '文章标题不能为空',
            },
            'digest': {
                'max_length': "文章摘要长度不能超过200",
                'min_length': "文章标题长度大于1",
                'required': '文章摘要不能为空',
            },
            'content': {
                'required': '文章内容不能为空',
            },
        }

class BannersAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.tagid = kwargs.pop("tagid", None)
        super().__init__(*args, **kwargs)
    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})

    news_id = forms.ModelChoiceField(queryset=News.objects.only('id').filter(is_delete=False),
                                     error_messages={"required": "文章id不能为空", "invalid_choice": "文章id不存在", })
    def clean_news_id(self):
        news_id = self.cleaned_data.get('news_id')
        if not (news_id in News.objects.only('id').filter(is_delete=False,tag_id=self.tagid)):
            raise forms.ValidationError('此新闻不在所选标签中')
        return news_id
    class Meta:
        model = Banner
        fields = ["image_url",'priority','news_id']
        error_messages = {
            'priority': {
                'required': '优先级不能为空',
                "invalid_choice": "此优先级不存在"
            },
            'news_id':{
                "invalid_choice": "此新闻不存在"
            }
        }

class BannersUpdateForm(forms.ModelForm):
    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})
    class Meta:
        model = Banner
        fields = ['image_url','priority']
        error_messages = {
            'priority': {
                'required': '优先级不能为空',
                "invalid_choice": "此优先级不存在"
            },


        }

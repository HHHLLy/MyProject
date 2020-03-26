from haystack import indexes
# from haystack import site

from .models import News



class NewsIndex(indexes.SearchIndex, indexes.Indexable):#类名是固定的:表名加Index
    """
    News索引数据模型类
    """
    text = indexes.CharField(document=True, use_template=True)
    # text是固定的 因为用的是txt文件
    # document为True是要用文档来建立索引 use_template是使用template模板里的text

    # 如果没有下面的字段 则查询到news对象后在使用的时候是news.object.id。。。 有下面字段的话直接 news.id
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    image_url = indexes.CharField(model_attr='image_url')
    # comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类
        """
        return News

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集
        """

        # return self.get_model().objects.filter(is_delete=False, tag_id=1)
        # 先建立小部分索引 因为建索引时间比较长 这样减少出错
        return  self.get_model().objects.filter(is_delete=False,tag_id__in=[1,2,3,4,5,6])
        # 建立所有tag_id索引 因为一共就6个tag_id



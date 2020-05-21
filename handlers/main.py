import tornado.web
class IndexHandlers(tornado.web.RequestHandler):
    """
    用户上传图片展示
    """
    def get(self):
        return self.write("首页")
class ExploreHandler(tornado.web.RequestHandler):
    """
    最近上传的图片页面
    """
    def get(self):
        return self.write("最近上传的页面")
class PostHandler(tornado.web.RequestHandler):
    """
    单个图片的详情页面
    """
    def get(self,post_id):
        return self.write("单个图片的详情页")
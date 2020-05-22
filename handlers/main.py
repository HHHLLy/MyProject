import tornado.web
from pycket.session import SessionMixin
from tornado.options import options
import os
from model.auth import *
class BaseHandlers(SessionMixin,tornado.web.RequestHandler):
    def get_current_user(self) :
        # print(self.session.get('user'))
        return self.session.get('user')
class IndexHandlers(tornado.web.RequestHandler):
    """
    用户上传图片展示
    """


    def get(self):
        post = session.query(Post).all()
        data = {
            "posts":post,
        }
        return self.render("index.html",**data)
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
class UploadHandler(BaseHandlers):

    @tornado.web.authenticated
    def get(self):

        return self.render('uploadimage.html')
    @tornado.web.authenticated
    def post(self):
        username = self.current_user
        upload_path = "static/upload"
        file_meta = self.request.files.get("img_file",[])
        for f in file_meta:
            file_name = f.get("filename")
            file_path = os.path.join(upload_path,file_name)
            # print(f.get("name"))
            # print(f.get("body"))
            with open(file_path,"wb") as ff:
                ff.write(f.get("body"))

            flg = Post.add_post(img_url=os.path.join("upload",file_name),username=username)
            self.write("上传成功" if flg else "没有此用户")


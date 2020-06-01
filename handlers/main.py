import tornado.web
from pycket.session import SessionMixin
from tornado.options import options
import uuid
import os

from PIL import Image
from model.auth import *
import json
class BaseHandlers(SessionMixin,tornado.web.RequestHandler):
    def get_current_user(self) :
        # print(self.session.get('user'))
        return self.session.get('user')
class IndexHandlers(BaseHandlers):
    """
    用户上传图片展示
    """
    def get(self):
        post_type = session.query(PostType).all()
        post = session.query(Post).all()
        data = {
            "posts":post,
            "post_type":post_type,
        }
        return  self.render("index.html",**data)

class ExploreHandler(BaseHandlers):
    """
    最近上传的图片页面
    """
    def get(self):
        return self.write("最近上传的页面")
class PostHandler(BaseHandlers):
    """
    单个图片的详情页面
    """
    def get(self,post_id):
        post = session.query(Post).filter_by(id=post_id).first()
        ptype_names = session.query(PostType).all()
        if post:
            return self.render("single.html",post=post,ptype_names=ptype_names)
        else:
            self.render("404.html")


class ImgUploadHandler(BaseHandlers):
    def post(self):

        image_upload_path = "static/upload"
        thumbnail_upload_path = "static/upload/thumbnail"
        file_meta = self.request.files.get("image_file",[])
        f = file_meta[0]


        image_type = f.get("filename").split(".")[-1]
        file_name = str(uuid.uuid1()) + "." + image_type
        file_path = os.path.join(image_upload_path,file_name)

        with open(file_path,"wb") as ff:
            ff.write(f.get("body"))



        im = Image.open(file_path)
        im.thumbnail((259.69,270))
        im.save(os.path.join(thumbnail_upload_path,file_name),image_type if image_type == "jpeg" else "png")
        thumbnail_url = os.path.join(thumbnail_upload_path, file_name)

        file_path = "/".join(file_path.split("/")[1:])
        thumbnail_url = "/".join(thumbnail_url.split("/")[1:])
        return self.write({"flag": "0","image_url":file_path,"thumbnail_url":thumbnail_url})
class UploadHandler(BaseHandlers):

    @tornado.web.authenticated
    def get(self):
        posttypes = session.query(PostType).all()
        return self.render('uploadimage.html',posttypes=posttypes)
    @tornado.web.authenticated
    def post(self):
        data =json.loads(self.request.body.decode())
        title = data.get("title")
        content = data.get("content")
        img_url = data.get("image_url")
        thumbnail_url = data.get("thumbnail_url")
        tag_id = data.get("tag_id")
        username = self.current_user



        flg = Post.add_post(title=title,content=content,img_url=img_url,
                            thumbnail_url=thumbnail_url,posttype_id=tag_id,
                            username=username)
        self.write({"flag":"0" if flg else "1"})

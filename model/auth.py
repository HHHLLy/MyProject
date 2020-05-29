from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import relationship
from model.db import Base
from model.db import session

class BaseModel:
    is_delete = Column(Boolean,default=False)
    createtime =  Column(DateTime,default=datetime.now())
    updatetime =  Column(DateTime,default=datetime.now())
class User(BaseModel,Base):
    __tablename__ = "user"
    id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(30),nullable=False,unique=True)
    password = Column(String(200),nullable=False)
    activation = Column(Boolean,default=False)
    email = Column(String(200))
    phone = Column(String(30),nullable=True,unique=True)
    @classmethod
    def add_user(cls,username,pwd,**kwargs):
        user = User(username=username,password=pwd, **kwargs)
        session.add(user)
        session.commit()
    @classmethod
    def check_user(cls,username):
        return session.query(User).filter_by(username=username).first()

    def __repr__(self):
        return "User:name={},pwd={}".format(self.username,self.password)

class PostType(BaseModel,Base):
    __tablename__ = "posttype"
    id = Column(Integer,autoincrement=True,primary_key=True)
    name = Column(String(20),unique=True)

class Post(BaseModel,Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String(300))
    thumbnail_url = Column(String(300))
    title = Column(String(300))
    content = Column(String(600))
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship("User",backref="post",uselist=False,cascade="all")
    type_id = Column(Integer, ForeignKey('posttype.id'))
    posttype = relationship("User", backref="posttype", uselist=False, cascade="all")
    @classmethod
    def add_post(cls,title,content,thumbnail_url,img_url,username,posttype_id):
        user = User.check_user(username)
        if not user:
            return False
        post = Post(title=title,content=content,thumbnail_url=thumbnail_url,image_url=img_url,user_id=user.id,type_id=posttype_id)
        session.add(post)
        session.commit()
        return True
    def __repr__(self):
        return "Post:title={}".format(self.title)
class Comment(BaseModel,Base):
    __tablename__ = "comment"
    id = Column(Integer,primary_key=True,autoincrement=True)
    content = Column(String(200))
    user_id = Column(Integer,ForeignKey("user.id"))
    post_id = Column(Integer,ForeignKey("post.id"))
    reply_id = Column(Integer,ForeignKey("comment.id"))
    up = Column(Integer)
    down = Column(Integer)






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

class Post(BaseModel,Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String(300))
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship("User",backref="post",uselist=False,cascade="all")
    @classmethod
    def add_post(cls,img_url,username):
        user = User.check_user(username)
        if not user:
            return False
        post = Post(image_url=img_url,user_id=user.id)
        session.add(post)
        session.commit()
        return True
    def __repr__(self):
        return "Post:user_id={}".format(self.user_id)




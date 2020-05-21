import tornado.web
from model.auth import *

class RegisterHandlers(tornado.web.RequestHandler):
    def get(self):
        return  self.render("register.html")
    def post(self):
        username = self.get_argument("username","").strip()
        pwd = self.get_argument('pwd','').strip()
        repeat_pwd = self.get_argument('repeat_pwd','').strip()
        if not all([username,pwd,repeat_pwd]):
            return  self.write("参数错误")
        if not (len(username) >= 0 and len(pwd) >= 6 and pwd == repeat_pwd):
            return  self.write("格式错误")
        a = User.check_user(username=username)
        print(a)
        if User.check_user(username):
            return self.write("用户名已存在")
        User.add_user(username=username,pwd=pwd)#入库
        return  self.redirect("/login")






class LoginHandlers(tornado.web.RequestHandler):
    def get(self):
        return  self.render("login.html")
    def post(self):
        pass
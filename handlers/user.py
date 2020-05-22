import tornado.web
from model.auth import *
from utils.account import *
from handlers.main import BaseHandlers
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

        if User.check_user(username):
            return self.write("用户名已存在")
        User.add_user(username=username,pwd=pas_encryption(pwd=pwd))#入库
        return  self.redirect("/login")






class LoginHandlers(BaseHandlers,tornado.web.RequestHandler):

    def get(self):
        return  self.render("login.html")
    def post(self):
        username = self.get_argument("username", "").strip()
        pwd = self.get_argument('pwd', '').strip()
        if not (username and pwd):
            return self.write("数据错误")
        user = User.check_user(username)
        if not user:
            return self.write("用户不存在")
        real_pwd = pas_encryption(pwd=pwd,encrypw=user.password,b=False)
        if not real_pwd:
            return self.write("密码错误")
        else:

            self.session.set("user",username)

            next_url = self.get_argument("next","/")
            print("next_url:"+next_url)
            return self.redirect(next_url)



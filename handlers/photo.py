import tornado.web
from handlers.main import BaseHandlers
from model.auth import *
class PhotographyHandler(BaseHandlers):
    def get(self):
        username = self.current_user
        user_obj = session.query(User).filter_by(username=username).first()


        return self.render("photography.html",user=user_obj)
class TravelHandler(BaseHandlers):
    def get(self):
        return self.render("travel.html")

class FashionHandler(BaseHandlers):
    def get(self):
        return self.render("fashion.html")

class AboutHandler(BaseHandlers):
    def get(self):
        return self.render("about.html")

class ContactHandler(BaseHandlers):
    def get(self):
        return self.render("contact.html")
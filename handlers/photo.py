import tornado.web
from handlers.main import BaseHandlers

class PhotographyHandler(BaseHandlers):
    def get(self):
        return self.render("photography.html")
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
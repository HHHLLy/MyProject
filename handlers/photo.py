import tornado.web


class PhotographyHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("photography.html")
class TravelHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("travel.html")

class FashionHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("fashion.html")

class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("about.html")

class ContactHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("contact.html")
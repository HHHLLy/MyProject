from tornado import ioloop
from tornado import web
import tornado.options
from handlers.main import IndexHandlers,ExploreHandler,PostHandler
from tornado.options import define,options
from handlers.user import *
define(name="port",default="8888",help="listenning port",type=int)
class Application(web.Application):
    def __init__(self):
        handlers = [
            (r"/",IndexHandlers),
            (r"/explore",ExploreHandler),
            (r"/post/(?P<post_id>[0-9]+)",PostHandler),
            (r"/register",RegisterHandlers),
            (r"/login",LoginHandlers),
        ]
        settings = dict(

            debug = True,
            template_path = "template"#由于app文件和template文件夹同级
        )
        super().__init__(handlers=handlers,**settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()

    Application().listen(options.port)
    ioloop.IOLoop.current().start()

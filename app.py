from tornado import ioloop
from tornado import web
import tornado.options
from handlers.main import *
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
            (r"/upload",UploadHandler)
        ]
        settings = dict(
            pycket={
                'engine': 'redis',
                'storage': {
                    'host': '127.0.0.1',
                    'port': 6379,
                    'db_sessions': 7,
                    'max_connections': 2 ** 31,
                },
                'cookies': {
                    # 设置过期时间
                    'expires_days': 2,
                    # 'expires':30, #毫秒
                },
            },
            login_url='/login',
            xsrf_cookies=True,
            cookie_secret='asdassaad-dda',
            debug = True,
            template_path = "template",#由于app文件和template文件夹同级
            static_path ="static",
        )
        super().__init__(handlers=handlers,**settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()

    Application().listen(options.port)
    ioloop.IOLoop.current().start()

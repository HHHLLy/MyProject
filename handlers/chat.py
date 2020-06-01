from typing import Union, Optional, Awaitable

import tornado.websocket
import tornado.web
from .main import BaseHandlers


class RoomHandler(BaseHandlers):
    '''
    聊天室
    '''
    def get(self):
        return self.render("room.html")
class EchoWebSocket(tornado.websocket.WebSocketHandler,BaseHandlers):
    waiter = set()
    @tornado.web.authenticated
    def open(self, *args: str, **kwargs: str) :
        
        self.waiter.add(self)
        for i in self.waiter:
            i.write_message("%s in home:"%self.current_user)

    def on_message(self, message: Union[str, bytes]):
        for i in self.waiter:
            i.write_message(u"%s said:%s"%(self.current_user,message))
            print(message)
    def on_close(self) -> None:
        self.waiter.remove(self)
        for i in self.waiter:
            i.write_message("%s out home:"%self.current_user)#此self时当前退出的EchoWebSocket对象 所以获取的也是退出的当前用户


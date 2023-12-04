# Stub for cursor support. 

from .remote import LGTVRemote
from ws4py.client.threadedclient import WebSocketClient


class LGTVCursor(WebSocketClient):

    def __finalize(self, response):
        address = response['payload']['socketPath']
        super(LGTVCursor, self).__init__(address, exclude_headers=["Origin"])

    def __init__(self, name, ip=None, mac=None, key=None, hostname=None):
        self.remote = LGTVRemote(name, ip, mac, key, hostname)
        self.remote.connect()
        self.remote.getCursorSocket(self.__finalize)

    def up(self):
        self.send("type:button\nname:UP\n\n")
        
    def down(self):
        self.send("type:button\nname:DOWN\n\n")

    def left(self):
        self.send("type:button\nname:LEFT\n\n")

    def right(self):
        self.send("type:button\nname:RIGHT\n\n")

    def click(self):
        self.send("type:click\n\n\n")

    def back(self):
        self.send("type:button\nname:BACK\n\n")

    def enter(self):
        self.remote.sendEnterKey()
    

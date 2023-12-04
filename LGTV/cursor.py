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

        self.remote.execute("getCursorSocket", callback=self.__finalize)

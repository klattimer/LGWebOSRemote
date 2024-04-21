# Stub for cursor support. 

import inspect
from time import sleep

from .remote import LGTVRemote
from ws4py.client.threadedclient import WebSocketClient


class LGTVCursor(WebSocketClient):

    def __finalize(self, response):
        self.remote.close()
        address = response['payload']['socketPath']
        super(LGTVCursor, self).__init__(address, exclude_headers=["Origin"])

    def __init__(self, name, ip=None, mac=None, key=None, hostname=None, ssl=False):
        self.remote = LGTVRemote(name, ip, mac, key, hostname, ssl)
        self.remote.connect()
        self.remote.execute("getCursorSocket", {"callback": self.__finalize})
        self.remote.run_forever()

    def _list_possible_buttons(self):
        buttons = []
        self_class = self.__class__.__name__

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("_"):
                continue

            if name in {"execute"}:
                continue

            if not method.__qualname__.startswith(f"{self_class}."):
                continue

            buttons.append(name)

        return buttons

    def execute(self, buttons):
        if not buttons:
            print("Add button presses to perform. Possible options:", ", ".join(self._list_possible_buttons()))
            return

        for i, button in enumerate(buttons):
            if not hasattr(self, button):
                print(f"{button} is not a possible button press, skipped")
                continue

            if i != 0:
                sleep(0.1)

            getattr(self, button)()

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
        self.send("type:button\nname:ENTER\n\n")

    def home(self):
        self.send("type:button\nname:HOME\n\n")

    def exit(self):
        self.send("type:button\nname:EXIT\n\n")

    def red(self):
        self.send("type:button\nname:RED\n\n")

    def green(self):
        self.send("type:button\nname:GREEN\n\n")

    def yellow(self):
        self.send("type:button\nname:YELLOW\n\n")

    def blue(self):
        self.send("type:button\nname:BLUE\n\n")

    def channel_up(self):
        self.send("type:button\nname:CHANNELUP\n\n")

    def channel_down(self):
        self.send("type:button\nname:CHANNELDOWN\n\n")

    def volume_up(self):
        self.send("type:button\nname:VOLUMEUP\n\n")

    def volume_down(self):
        self.send("type:button\nname:VOLUMEDOWN\n\n")

    def play(self):
        self.send("type:button\nname:PLAY\n\n")

    def pause(self):
        self.send("type:button\nname:PAUSE\n\n")

    def stop(self):
        self.send("type:button\nname:STOP\n\n")

    def rewind(self):
        self.send("type:button\nname:REWIND\n\n")

    def fast_forward(self):
        self.send("type:button\nname:FASTFORWARD\n\n")

    def asterisk(self):
        self.send("type:button\nname:ASTERISK\n\n")

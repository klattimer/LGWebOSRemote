from time import sleep
import json
import logging

from ws4py.client.threadedclient import WebSocketClient

from remote import LGTVRemote


class LGTVInStart(WebSocketClient):
    # The factory menus (In-Start, EZ Adjust) live in com.webos.app.factorywin
    # but stay invisible unless launched with the executeFactory trigger and
    # unlocked by sending the service PIN over the pointer input socket.

    def __finalize(self, response):
        payload = response.get("payload", {})
        if payload.get("socketPath"):
            super(LGTVInStart, self).__init__(payload["socketPath"], exclude_headers=["Origin"])
            self.__ready = True
        else:
            print(json.dumps(response))
        self.remote.close()

    def __launchResult(self, response):
        if not response.get("payload", {}).get("returnValue"):
            print(json.dumps(response))

    def __init__(self, name, ip=None, mac=None, key=None, hostname=None, ssl=False, irKey="inStart"):
        self.__ready = False
        self.__irKey = irKey

        self.remote = LGTVRemote(name, ip, mac, key, hostname, ssl)
        self.remote.connect()
        self.remote.execute("openAppWithPayload", {
            "payload": {
                "id": "com.webos.app.factorywin",
                "params": {"id": "executeFactory", "irKey": irKey}
            },
            "callback": self.__launchResult
        })
        self.remote.execute("getCursorSocket", {"callback": self.__finalize})
        self.remote.run_forever()

    def unlock(self, pin="0413"):
        if not self.__ready:
            logging.error("Could not open the factory menu")
            return
        # factorywin needs a moment before it listens for the PIN
        sleep(2)
        self.connect()
        for digit in str(pin):
            self.send("type:button\nname:%s\n\n" % digit)
            sleep(0.3)
        sleep(0.5)
        self.close()
        print(json.dumps({
            "factoryMenu": {
                "irKey": self.__irKey,
                "pin": str(pin),
            }
        }))

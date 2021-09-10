from ws4py.client.threadedclient import WebSocketClient
from getmac import get_mac_address
import subprocess
import socket
import re
import json

from .payload import hello_data


class LGTVAuth(WebSocketClient):
    def __init__(self, name, host):
        self.__clientKey = None
        self.__macAddress = None
        self.__name = name
        self.__handshake_done = False

        # Check if host is an IP address or hostname
        # Try to resolve the hostname
        try:
            socket.inet_aton(host)
            self.__ip = host
            self.__hostname = socket.gethostbyaddr(host)[0]
        except:
            self.__hostname = host
            self.__ip = socket.gethostbyname(host)

        if self.__macAddress is None and self.__ip is not None:
            self.__macAddress = self.__get_mac_address(self.__ip)

        super(LGTVAuth, self).__init__('ws://' + self.__ip + ':3000/', exclude_headers=["Origin"])
        self.__waiting_callback = self.__prompt

    def opened(self):
        self.send(json.dumps(hello_data))

    def __prompt(self, response):
        # {"type":"response","id":"register_0","payload":{"pairingType":"PROMPT","returnValue":true}}
        if response['payload']['pairingType'] == "PROMPT":
            print ("Please accept the pairing request on your LG TV")
            self.__waiting_callback = self.__set_client_key

    def __set_client_key(self, response):
        # {"type":"registered","id":"register_0","payload":{"client-key":"a40635497f685492b8366e208808a86b"}}
        if 'client-key' in response['payload'].keys():
            self.__clientKey = response['payload']['client-key']
            self.__waiting_callback = None
            self.close()
            return

    def __get_mac_address(self, address):
        return get_mac_address(ip=address)

    def received_message(self, response):
        if self.__waiting_callback:
            self.__waiting_callback(json.loads(str(response)))

    def closed(self, code, reason=None):
        print (json.dumps({
            "closing": {
                "code": code,
                "reason": reason.decode('utf-8')
            }
        }))

    def serialise(self):
        return {
            "key": self.__clientKey,
            "mac": self.__macAddress,
            "ip": self.__ip,
            "hostname": self.__hostname
        }

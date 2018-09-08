# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
from types import FunctionType
from wakeonlan import wol
import json
import socket
import subprocess
import re
import os
import sys
import urllib

class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

hello_data = {
    "id": "register_0",
    "payload": {
        "forcePairing": False,
        "manifest": {
            "appVersion": "1.1",
            "manifestVersion": 1,
            "permissions": [
                "LAUNCH",
                "LAUNCH_WEBAPP",
                "APP_TO_APP",
                "CLOSE",
                "TEST_OPEN",
                "TEST_PROTECTED",
                "CONTROL_AUDIO",
                "CONTROL_DISPLAY",
                "CONTROL_INPUT_JOYSTICK",
                "CONTROL_INPUT_MEDIA_RECORDING",
                "CONTROL_INPUT_MEDIA_PLAYBACK",
                "CONTROL_INPUT_TV",
                "CONTROL_POWER",
                "READ_APP_STATUS",
                "READ_CURRENT_CHANNEL",
                "READ_INPUT_DEVICE_LIST",
                "READ_NETWORK_STATE",
                "READ_RUNNING_APPS",
                "READ_TV_CHANNEL_LIST",
                "WRITE_NOTIFICATION_TOAST",
                "READ_POWER_STATE",
                "READ_COUNTRY_INFO"
            ],
            "signatures": [
                {
                    "signature": "eyJhbGdvcml0aG0iOiJSU0EtU0hBMjU2Iiwia2V5SWQiOiJ0ZXN0LXNpZ25pbmctY2VydCIsInNpZ25hdHVyZVZlcnNpb24iOjF9.hrVRgjCwXVvE2OOSpDZ58hR+59aFNwYDyjQgKk3auukd7pcegmE2CzPCa0bJ0ZsRAcKkCTJrWo5iDzNhMBWRyaMOv5zWSrthlf7G128qvIlpMT0YNY+n/FaOHE73uLrS/g7swl3/qH/BGFG2Hu4RlL48eb3lLKqTt2xKHdCs6Cd4RMfJPYnzgvI4BNrFUKsjkcu+WD4OO2A27Pq1n50cMchmcaXadJhGrOqH5YmHdOCj5NSHzJYrsW0HPlpuAx/ECMeIZYDh6RMqaFM2DXzdKX9NmmyqzJ3o/0lkk/N97gfVRLW5hA29yeAwaCViZNCP8iC9aO0q9fQojoa7NQnAtw==",
                    "signatureVersion": 1
                }
            ],
            "signed": {
                "appId": "com.lge.test",
                "created": "20140509",
                "localizedAppNames": {
                    "": "LG Remote App",
                    "ko-KR": u"리모컨 앱",
                    "zxx-XX": u"ЛГ Rэмotэ AПП"
                },
                "localizedVendorNames": {
                    "": "LG Electronics"
                },
                "permissions": [
                    "TEST_SECURE",
                    "CONTROL_INPUT_TEXT",
                    "CONTROL_MOUSE_AND_KEYBOARD",
                    "READ_INSTALLED_APPS",
                    "READ_LGE_SDX",
                    "READ_NOTIFICATIONS",
                    "SEARCH",
                    "WRITE_SETTINGS",
                    "WRITE_NOTIFICATION_ALERT",
                    "CONTROL_POWER",
                    "READ_CURRENT_CHANNEL",
                    "READ_RUNNING_APPS",
                    "READ_UPDATE_INFO",
                    "UPDATE_FROM_REMOTE_APP",
                    "READ_LGE_TV_INPUT_EVENTS",
                    "READ_TV_CURRENT_TIME"
                ],
                "serial": "2f930e2d2cfe083771f68e4fe7bb07",
                "vendorId": "com.lge"
            }
        },
        "pairingType": "PROMPT"
    },
    "type": "register"
}


def LGTVScan(first_only=False):
    request = 'M-SEARCH * HTTP/1.1\r\n' \
              'HOST: 239.255.255.250:1900\r\n' \
              'MAN: "ssdp:discover"\r\n' \
              'MX: 2\r\n' \
              'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    addresses = []
    attempts = 4
    while attempts > 0:
        sock.sendto(request, ('239.255.255.250', 1900))
        uuid = None
        model = None
        address = None
        data = {}
        try:
            response, address = sock.recvfrom(512)
            # print response
            for line in response.split('\n'):
                if line.startswith("USN"):
                    uuid = re.findall(r'uuid:(.*?):', line)[0]
                if line.startswith("DLNADeviceName"):
                    (junk, data) = line.split(':')
                    data = data.strip()
                    data = urllib.unquote(data)
                    model = re.findall(r'\[LG\] webOS TV (.*)', data)[0]
                data = HashableDict({
                    'uuid': uuid,
                    'model': model,
                    'address': address[0]
                })
        except Exception as e:
            print e.message
            attempts -= 1
            continue

        if re.search('LG', response):
            if first_only:
                sock.close()
                return data
            else:
                addresses.append(data)

        attempts -= 1

    sock.close()
    if first_only:
        return []

    if len(addresses) == 0:
        return []

    return list(set(addresses))


def resolveHost(hostname):
    return socket.gethostbyname(hostname)


def getMacAddress(address):
    pid = subprocess.Popen(["arp", "-n", address], stdout=subprocess.PIPE)
    s = pid.communicate()[0]
    matches = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s)
    if not matches:
        return None
    mac = matches.groups()[0]
    m = mac.split(':')
    mac = ':'.join(['%02x' % int(x, 16) for x in m])
    return mac


def methods(cls):
    return [x for x, y in cls.__dict__.items() if type(y) == FunctionType]


def getCommands(cls):
    excludes = [
        'opened',
        'closed',
        'received_message',
        'exec_command'
    ]
    out = []
    m = methods(cls)
    for method in m:
        if method.startswith("_" + cls.__name__):
            continue
        if method in excludes:
            continue
        if method.startswith("__"):
            continue
        out.append(method)
    out.sort()
    return out


class LGTVClient(WebSocketClient):
    def __init__(self, hostname=None):
        self.__command_count = 0
        self.__waiting_callback = None
        if os.path.exists(os.path.expanduser("~/.lgtv.json")):
            f = open(os.path.expanduser("~/.lgtv.json"))
            settings = json.loads(f.read())
            f.close()
            self.__hostname = settings['hostname']
            self.__clientKey = settings["client-key"]
            self.__ip = settings['ip']
            self.__macAddress = settings['mac-address']
            if not self.__macAddress and self.__ip is not None:
                self.__macAddress = getMacAddress(self.__ip)
                self.__store_settings()
        else:
            self.__hostname = hostname
            if hostname is not None:
                self.__clientKey = None
                self.__ip = resolveHost(hostname)
                self.__macAddress = getMacAddress(self.__ip)
                self.__store_settings()
            else:
                self.__ip = None
        self.__handshake_done = False
        super(LGTVClient, self).__init__('ws://' + self.__hostname + ':3000/', exclude_headers=["Origin"])
        self.__waiting_command = None

    def __exec_command(self):
        if self.__handshake_done is False:
            print "Error: Handshake failed"
        if self.__waiting_command is None or len(self.__waiting_command.keys()) == 0:
            self.close()
            return
        command = self.__waiting_command.keys()[0]
        args = self.__waiting_command[command]
        self.__class__.__dict__[command](self, **args)

    def exec_command(self, command, args):
        if command not in self.__class__.__dict__.keys():
            usage("Invalid command")
        self.__waiting_command = {command: args}

    def __store_settings(self):
        data = {
            "client-key": self.__clientKey,
            "mac-address": self.__macAddress,
            "ip": self.__ip,
            "hostname": self.__hostname
        }
        f = open(os.path.expanduser("~/.lgtv.json"), "w")
        f.write(json.dumps(data))
        f.close()

    def opened(self):
        if self.__clientKey:
            hello_data['payload']['client-key'] = self.__clientKey
            self.__waiting_callback = self.__handshake
        else:
            self.__waiting_callback = self.__prompt
        self.send(json.dumps(hello_data))

    def closed(self, code, reason=None):
        print json.dumps({
            "closing": {
                "code": code,
                "reason": reason
            }
        })

    def received_message(self, response):
        if self.__waiting_callback:
            self.__waiting_callback(json.loads(str(response)))

    def __defaultHandler(self, response):
        # {"type":"response","id":"0","payload":{"returnValue":true}}
        if response['type'] == "error":
            print json.dumps(response)
            self.close()
        if "returnValue" in response["payload"] and response["payload"]["returnValue"] is True:
            print json.dumps(response)
            self.close()
        else:
            print json.dumps(response)

    def __prompt(self, response):
        # {"type":"response","id":"register_0","payload":{"pairingType":"PROMPT","returnValue":true}}
        if response['payload']['pairingType'] == "PROMPT":
            print "Please accept the pairing request on your LG TV"
            self.__waiting_callback = self.__set_client_key

    def __handshake(self, response):
        if 'client-key' in response['payload'].keys():
            self.__handshake_done = True
            self.__exec_command()

    def __set_client_key(self, response):
        # {"type":"registered","id":"register_0","payload":{"client-key":"a40635497f685492b8366e208808a86b"}}
        if 'client-key' in response['payload'].keys():
            self.__clientKey = response['payload']['client-key']
            self.__waiting_callback = None
            self.__store_settings()
        self.__handshake(response)

    def on(self):
        if not self.__macAddress:
            print "Client must have been powered on and paired before power on works"
        wol.send_magic_packet(self.__macAddress)

    def off(self):
        self.__send_command("", "request", "ssap://system/turnOff")

    def openBrowserAt(self, url, callback=None):
        self.__send_command("", "request", "ssap://system.launcher/open", {"target": url}, callback)

    def notification(self, message, callback=None):
        self.__send_command("", "request", "ssap://system.notifications/createToast", {"message": message}, callback)

    def mute(self, muted=True, callback=None):
        self.__send_command("", "request", "ssap://audio/setMute", {"mute": muted}, callback)

    def audioStatus(self, callback=None):
        self.__send_command("status_", "request", "ssap://audio/getStatus", None, callback)

    def audioVolume(self, callback=None):
        self.__send_command("status_", "request", "ssap://audio/getVolume", None, callback)

    def setVolume(self, level, callback=None):
        self.__send_command("", "request", "ssap://audio/setVolume", {"volume": level}, callback)

    def volumeUp(self, callback=None):
        self.__send_command("volumeup_", "request", "ssap://audio/volumeUp", None, callback)

    def volumeDown(self, callback=None):
        self.__send_command("volumedown_", "request", "ssap://audio/volumeDown", None, callback)

    def inputMediaPlay(self, callback=None):
        self.__send_command("", "request", "ssap://media.controls/play", None, callback)

    def inputMediaStop(self, callback=None):
        self.__send_command("", "request", "ssap://media.controls/stop", None, callback)

    def inputMediaPause(self, callback=None):
        self.__send_command("", "request", "ssap://media.controls/pause", None, callback)

    def inputMediaRewind(self, callback=None):
        self.__send_command("", "request", "ssap://media.controls/rewind", None, callback)

    def inputMediaFastForward(self, callback=None):
        self.__send_command("", "request", "ssap://media.controls/fastForward", None, callback)

    def inputChannelUp(self, callback=None):
        self.__send_command("", "request", "ssap://tv/channelUp", None, callback)

    def inputChannelDown(self, callback=None):
        self.__send_command("", "request", "ssap://tv/channelDown", None, callback)

    def setTVChannel(self, channel, callback=None):
        self.__send_command("", "request", "ssap://tv/openChannel", {"channelId": channel}, callback)

    def getTVChannel(self, callback=None):
        self.__send_command("channels_", "request", "ssap://tv/getCurrentChannel", None, callback)

    def listChannels(self, callback=None):
        self.__send_command("channels_", "request", "ssap://tv/getChannelList", None, callback)

    def input3DOn(self, callback=None):
        self.__send_command("", "request", "ssap://com.webos.service.tv.display/set3DOn", None, callback)

    def input3DOff(self, callback=None):
        self.__send_command("", "request", "ssap://com.webos.service.tv.display/set3DOff", None, callback)

    def listInputs(self, callback=None):
        self.__send_command("input_", "request", "ssap://tv/getExternalInputList", None, callback)

    def setInput(self, input_id, callback=None):
        self.__send_command("", "request", "ssap://tv/switchInput", {"inputId": input_id}, callback)

    def swInfo(self, callback=None):
        self.__send_command("sw_info_", "request", "ssap://com.webos.service.update/getCurrentSWInformation", None, callback)

    def listServices(self, callback=None):
        self.__send_command("services_", "request", "ssap://api/getServiceList", None, callback)

    def listApps(self, callback=None):
        self.__send_command("launcher_", "request", "ssap://com.webos.applicationManager/listLaunchPoints", None, callback)

    def openAppWithPayload(self, payload, callback=None):
        self.__send_command("", "request", "ssap://com.webos.applicationManager/launch", payload, callback)

    def startApp(self, appid, callback=None):
        self.__send_command("", "request", "ssap://system.launcher/launch", {'id': appid}, callback)

    def closeApp(self, appid, callback=None):
        self.__send_command("", "request", "ssap://system.launcher/close", {'id': appid}, callback)

    def openYoutubeId(self, videoid, callback=None):
        self.openYoutubeURL("http://www.youtube.com/tv?v=" + videoid, callback)

    def openYoutubeURL(self, url, callback=None):
        payload = {"id": "youtube.leanback.v4", "params": {"contentTarget": url}}
        self.__send_command("", "request", "ssap://system.launcher/launch", payload, callback)

    def __send_command(self, prefix, msgtype, uri, payload=None, callback=None):
        if not callback:
            callback = self.__defaultHandler
        self.__waiting_callback = callback
        message_data = {
            'id': prefix + str(self.__command_count),
            'type': msgtype,
            'uri': uri
        }
        if type(payload) == dict:
            payload = json.dumps(payload)
        if type(payload) == str and len(payload) > 0:
            message_data['payload'] = payload

        self.send(json.dumps(message_data))

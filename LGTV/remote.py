from ws4py.client.threadedclient import WebSocketClient
from types import FunctionType
from urllib.parse import parse_qs, urlparse
from wakeonlan import send_magic_packet
import socket
import requests
import base64
import json
import os
import logging

from .payload import hello_data


class LGTVRemote(WebSocketClient):
    @classmethod
    def getCommands(cls):
        excludes = [
            'opened',
            'closed',
            'received_message',
            'exec_command',
            'getCommands'
        ]
        out = []
        m = [x for x, y in cls.__dict__.items() if type(y) == FunctionType]
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

    def __init__(self, name, ip=None, mac=None, key=None, hostname=None):
        self.__command_count = 0
        self.__waiting_callback = None
        self.__commands = []
        self.__handshake_done = False

        self.__hostname = hostname
        self.__clientKey = key
        self.__macAddress = mac
        self.__ip = ip
        self.__name = name

        if self.__hostname is not None:
            # Over ride IP address when we know the hostname
            self.__ip = socket.gethostbyname(self.__hostname)

        super(LGTVRemote, self).__init__('ws://' + self.__ip + ':3000/', exclude_headers=["Origin"])

    def execute(self, command, args):
        self.__commands.append({command: args})
        if self.__handshake_done is True:
            self.__execute()

    def serialise(self):
        return {
            self.__name: {
                "key": self.__clientKey,
                "mac": self.__macAddress,
                "ip": self.__ip,
                "hostname": self.__hostname
            }
        }

    #
    # Pragma Mark WebSocketClient subclass
    #

    def opened(self):
        if self.__clientKey is None:
            raise Exception("Client is not authenticated")

        logging.debug("Initiating handshake")
        hello_data['payload']['client-key'] = self.__clientKey
        self.__waiting_callback = self.__handshake
        self.send(json.dumps(hello_data))

    def closed(self, code, reason: str = ''):
        if type(reason) == bytes:
            reason = reason.decode('utf-8')
        print (json.dumps({
            "closing": {
                "code": code,
                "reason": str(reason)
            }
        }))

    def received_message(self, response):
        logging.debug("Received response")
        logging.debug(response)
        if self.__waiting_callback:
            self.__waiting_callback(json.loads(str(response)))

    #
    # Pragma Mark Internal command handling
    #
    def __handshake(self, response):
        if 'client-key' in response['payload'].keys():
            logging.debug("Handshake complete")
            self.__handshake_done = True
            self.__execute()

    def __execute(self):
        if self.__handshake_done is False:
            print ("Error: Handshake failed")

        while len(self.__commands) > 0:
            command = self.__commands.pop(0)
            method = list(command.keys())[0]
            args = command[method]
            self.__class__.__dict__[method](self, **args)
        # self.__waitClose()

    def __waitClose(self):
        self._th.join(timeout=1)
        self.close()

    def __defaultHandler(self, response):
        logging.debug(response)
        # {"type":"response","id":"0","payload":{"returnValue":true}}
        if response['type'] == "error":
            print (json.dumps(response))
            self.close()
        if "returnValue" in response["payload"] and response["payload"]["returnValue"] is True:
            print (json.dumps(response))
            self.close()
        else:
            print (json.dumps(response))

    def __send_command(self, msgtype, uri, payload=None, callback=None, prefix=None):
        if not callback:
            callback = self.__defaultHandler
        self.__waiting_callback = callback
        if prefix is None:
            messageid = str(self.__command_count)
        else:
            messageid = prefix + '_' + str(self.__command_count)

        message_data = {
            'id': messageid,
            'type': msgtype,
            'uri': uri
        }
        if type(payload) == dict:
            payload = json.dumps(payload)

        if type(payload) == str and len(payload) > 2:
            message_data['payload'] = payload

        self.__command_count += 1
        logging.debug(message_data)
        self.send(json.dumps(message_data))

    def __get_youtube_id_from_url(self, url_string):
        if url_string.startswith(("youtu", "www")):
            url_string = "http://" + url_string
        url = urlparse(url_string)

        if url.hostname and url.path:
            if "youtube" in url.hostname:
                if url.path == "/watch":
                    return parse_qs(url.query)["v"][0]
                elif url.path.startswith(("/embed/", "/v/")):
                    return url.path.split("/")[2]
            elif "youtu.be" in url.hostname:
                return url.path[1:]
        # No ID found
        return None

    #
    # Pragma Mark Supported commands
    #
    def on(self):
        if not self.__macAddress:
            print ("Client must have been powered on and paired before power on works")
        send_magic_packet(self.__macAddress)

    def off(self):
        self.__send_command("request", "ssap://system/turnOff")

    def openBrowserAt(self, url, callback=None):
        self.__send_command("request", "ssap://system.launcher/open", {"target": url}, callback)

    def notification(self, message, callback=None):
        self.__send_command("request", "ssap://system.notifications/createToast", {"message": message}, callback)

	# not working, why?
    #def notificationClose(self, toastId, callback=None):
        #self.__send_command("request", "ssap://system.notifications/closeToast", {'toastId': toastId}, callback)

    def notificationWithIcon(self, message, url, callback=None):
        if os.path.exists(url):
            with open(url) as f:
                content = f.read()
        else:
            content = requests.get(url).content
        data = base64.b64encode(content)
        data = {"iconData": data, "iconExtension": "png", "message": message}
        self.__send_command("request", "ssap://system.notifications/createToast", data, callback)

    def mute(self, muted, callback=None):
        self.__send_command("request", "ssap://audio/setMute", {"mute": muted}, callback)

    def audioStatus(self, callback=None):
        self.__send_command("request", "ssap://audio/getStatus", None, callback, "status")

    def audioVolume(self, callback=None):
        self.__send_command("request", "ssap://audio/getVolume", None, callback, "status")

    def setVolume(self, level, callback=None):
        self.__send_command("request", "ssap://audio/setVolume", {"volume": level}, callback)

    def volumeUp(self, callback=None):
        self.__send_command("request", "ssap://audio/volumeUp", None, callback, "volumeup")

    def volumeDown(self, callback=None):
        self.__send_command("request", "ssap://audio/volumeDown", None, callback, "volumedown")

    def inputMediaPlay(self, callback=None):
        self.__send_command("request", "ssap://media.controls/play", None, callback)

    def inputMediaStop(self, callback=None):
        self.__send_command("request", "ssap://media.controls/stop", None, callback)

    def inputMediaPause(self, callback=None):
        self.__send_command("request", "ssap://media.controls/pause", None, callback)

    def inputMediaRewind(self, callback=None):
        self.__send_command("request", "ssap://media.controls/rewind", None, callback)

    def inputMediaFastForward(self, callback=None):
        self.__send_command("request", "ssap://media.controls/fastForward", None, callback)

    def inputChannelUp(self, callback=None):
        self.__send_command("request", "ssap://tv/channelUp", None, callback)

    def inputChannelDown(self, callback=None):
        self.__send_command("request", "ssap://tv/channelDown", None, callback)

    def setTVChannel(self, channel, callback=None):
        self.__send_command("request", "ssap://tv/openChannel", {"channelId": channel}, callback)

    def getTVChannel(self, callback=None):
        self.__send_command("request", "ssap://tv/getCurrentChannel", None, callback, "channels")

    def listChannels(self, callback=None):
        self.__send_command("request", "ssap://tv/getChannelList", None, callback, "channels")

    def getCursorSocket(self, callback=None):
        self.__send_command("request", "ssap://com.webos.service.networkinput/getPointerInputSocket", None, callback)

    def input3DOn(self, callback=None):
        self.__send_command("request", "ssap://com.webos.service.tv.display/set3DOn", None, callback)

    def input3DOff(self, callback=None):
        self.__send_command("request", "ssap://com.webos.service.tv.display/set3DOff", None, callback)

    def listInputs(self, callback=None):
        self.__send_command("request", "ssap://tv/getExternalInputList", None, callback, "input")

    def setInput(self, input_id, callback=None):
        self.__send_command("request", "ssap://tv/switchInput", {"inputId": input_id}, callback)

    def swInfo(self, callback=None):
        self.__send_command("request", "ssap://com.webos.service.update/getCurrentSWInformation", None, callback, "sw_info")

    def listServices(self, callback=None):
        self.__send_command("request", "ssap://api/getServiceList", None, callback, "services")

    def listLaunchPoints(self, callback=None):
        self.__send_command("request", "ssap://com.webos.applicationManager/listLaunchPoints", None, callback, "launcher")

    def openAppWithPayload(self, payload, callback=None):
        self.__send_command("request", "ssap://com.webos.applicationManager/launch", payload, callback)

    def startApp(self, appid, callback=None):
        self.__send_command("request", "ssap://system.launcher/launch", {'id': appid}, callback)

    def closeApp(self, appid, callback=None):
        self.__send_command("request", "ssap://system.launcher/close", {'id': appid}, callback)

    def openYoutubeId(self, videoid, callback=None):
        self.openYoutubeURL("http://www.youtube.com/tv?v=" + videoid, callback)

    def openYoutubeURL(self, url, callback=None):
        payload = {"id": "youtube.leanback.v4", "params": {"contentTarget": url}}
        self.__send_command("request", "ssap://system.launcher/launch", payload, callback)

    def openYoutubeLegacyId(self, videoid, callback=None):
        payload = {"id": "youtube.leanback.v4", "contentId": videoid}
        self.__send_command("request", "ssap://system.launcher/launch", payload, callback)

    def openYoutubeLegacyURL(self, url, callback=None):
        videoid = self.__get_youtube_id_from_url(url)
        if videoid:
            self.openYoutubeLegacyId(videoid, callback)
        else:
            logging.debug("Invalid Youtube video URL: " + url)
            print("Invalid Youtube video URL")
            self.close()

    def getForegroundAppInfo(self, callback=None):
        self.__send_command("request", "ssap://com.webos.applicationManager/getForegroundAppInfo", None, callback)

    def getPowerState(self, callback=None):
        self.__send_command("request", "ssap://com.webos.service.tvpower/power/getPowerState", None, callback)

    def getSoundOutput(self, callback=None):
        self.__send_command("request", "ssap://com.webos.service.apiadapter/audio/getSoundOutput", None, callback)

    def getSystemInfo(self, callback=None):
        self.__send_command("request", "ssap://system/getSystemInfo", None, callback)

    def listApps(self, callback=None):
        self.__send_command("request", "ssap://com.webos.applicationManager/listApps", None, callback)

    def setSoundOutput(self, output, callback=None):
        self.__send_command("request", "ssap://audio/changeSoundOutput", {"output": output}, callback)

    def screenOff(self):
        self.__send_command("request", "ssap://com.webos.service.tvpower/power/turnOffScreen", {"standbyMode": "active"})

    def screenOn(self):
        self.__send_command("request", "ssap://com.webos.service.tvpower/power/turnOnScreen", {"standbyMode": "active"})

    def getPictureSettings(self, keys=["contrast", "backlight", "brightness", "color"]):
        self.__send_command("request", "ssap://settings/getSystemSettings", {"category": "picture", "keys": keys})

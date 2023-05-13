# LGWebOSRemote
Command line webOS remote for LGTVs. This tool uses a connection via websockets to port 3000 on newer LG TVs, there are other tools which use a restful connection to port 8080 however that port is closed on newer firmware versions.

## Supported models

### Tested with

  * 43LM6300PSB
  * 43UN73003LC
  * 60UJ6300-UA
  * HU80KG.AEU (CineBeam 4K)
  * OLED55B7
  * OLED55C9
  * OLED55CX5LB
  * OLED55CXAUA
  * OLED65B9PUA
  * OLED77CX9LA
  * OLED77GX
  * OLED42C2 (ssl)
  * OLED48C2 (ssl)
  * SK8500PLA
  * SM9010PLA
  * UF776V
  * UF830V
  * UH650V
  * UJ6309
  * UJ635V
  * UJ6570
  * UJ701V
  * [please add more!]

Tested with python 2.7 on mac/linux and works fine, your mileage may vary with windows, patches welcome.
Tested with python 3.9 on Debian Unstable.
Tested with python 3.10 on Windows 10/11
Tested with 3.10 on WSL (Ubuntu 20.04)

### Likely supports

All devices with firmware major version 4, product name "webOSTV 2.0"

## Available Commands
	lgtv scan
	lgtv auth <host> MyTV
	lgtv MyTV audioStatus
	lgtv MyTV audioVolume
	lgtv MyTV closeAlert <alertId>
	lgtv MyTV closeApp <appid>
	lgtv MyTV createAlert <message> <button>
	lgtv MyTV execute <command>
	lgtv MyTV getCursorSocket
	lgtv MyTV getForegroundAppInfo
	lgtv MyTV getPictureSettings
	lgtv MyTV getPowerState
	lgtv MyTV getSoundOutput
	lgtv MyTV getSystemInfo
	lgtv MyTV getTVChannel
	lgtv MyTV input3DOff
	lgtv MyTV input3DOn
	lgtv MyTV inputChannelDown
	lgtv MyTV inputChannelUp
	lgtv MyTV inputMediaFastForward
	lgtv MyTV inputMediaPause
	lgtv MyTV inputMediaPlay
	lgtv MyTV inputMediaRewind
	lgtv MyTV inputMediaStop
	lgtv MyTV listApps
	lgtv MyTV listLaunchPoints
	lgtv MyTV listChannels
	lgtv MyTV listInputs
	lgtv MyTV listServices
	lgtv MyTV mute <true|false>
	lgtv MyTV notification <message>
	lgtv MyTV notificationWithIcon <message> <url>
	lgtv MyTV off
	lgtv MyTV on
	lgtv MyTV openAppWithPayload <payload>
	lgtv MyTV openBrowserAt <url>
	lgtv MyTV openYoutubeId <videoid>
	lgtv MyTV openYoutubeURL <url>
	lgtv MyTV openYoutubeLegacyId <videoid>
	lgtv MyTV openYoutubeLegacyURL <url>
	lgtv MyTV serialise
	lgtv MyTV setInput <input_id>
	lgtv MyTV setSoundOutput <tv_speaker|external_optical|external_arc|external_speaker|lineout|headphone|tv_external_speaker|tv_speaker_headphone|bt_soundbar>
	lgtv MyTV screenOff
	lgtv MyTV screenOn
	lgtv MyTV setTVChannel <channelId>
	lgtv MyTV setVolume <level>
	lgtv MyTV startApp <appid>
	lgtv MyTV swInfo
	lgtv MyTV volumeDown
	lgtv MyTV volumeUp

## Install

Requires wakeonlan, websocket for python (python3-websocket for python3), and getmac.
python-pip (python3-pip for python3) and git are required for the installation process.

    python -m venv lgtv-venv
    source lgtv-venv/bin/activate
    pip install git+https://github.com/klattimer/LGWebOSRemote

To install it system wide:

	sudo mkdir -p /opt
	sudo python -m venv /opt/lgtv-venv
	source /opt/lgtv-venv/bin/activate
	sudo pip install git+https://github.com/klattimer/LGWebOSRemote

## Example usage
    # Scan/Authenticate
    $ lgtv scan
    {
        "count": 1,
        "list": [
            {
                "address": "192.168.1.31",
                "model": "UF830V",
                "uuid": "10f34f86-0664-f223-4b8f-d16a772d9baf"
            }
        ],
        "result": "ok"
    }
    $ lgtv auth 192.168.1.31 MyTV
    # At this point the TV will request pairing, follow the instructions on screen

    # Commands are basically
    #$ lgtv TVNAME COMMAND COMMAND ARGS

    $ lgtv MyTV on
    $ lgtv MyTV off

    # If you have the youtube plugin
    $ lgtv MyTV openYoutubeURL https://www.youtube.com/watch?v=dQw4w9WgXcQ

    # Otherwise, this works reasonably well
    $ lgtv MyTV openBrowserAt https://www.youtube.com/tv#/watch?v=dQw4w9WgXcQ

## SSL

Starting 25th of January 2023 LG has deprecated insecure ws connections, ssl is now required. Because of this, should you wish to use it on newer firmware devices you can append the argument "ssl" at the back. It connects to 3001 with wss. 
### Example
```
$ lgtv auth 192.168.1.31 MyTV ssl 
$ lgtv MyTV off ssl
$ lgtv MyTV screenOff ssl
```

## Caveats

You need to auth with the TV before being able to use the on command as it requires the mac address.

## TODO

Implement the following features:

	closeToast
	getSystemSettings

## Bugs

I couldn't test youtube because it seems the app isn't installed and not available to download right now
maybe they're updating it?

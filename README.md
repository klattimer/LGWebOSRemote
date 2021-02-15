# LGWebOSRemote
Command line webOS remote for LGTVs. This tool uses a connection via websockets to port 3000 on newer LG TVs, there are other tools which use a restful connection to port 8080 however that port is closed on newer firmware versions.

## Supported models

### Tested with

  * UF830V
  * UH650V
  * UJ635V
  * UJ6309
  * UJ6570
  * UF776V
  * HU80KG.AEU (CineBeam 4K)
  * OLED55B7
  * SK8500PLA
  * SM9010PLA
  * OLED65B9PUA
  * OLED55C9
  * OLED55CXAUA
  * 43LM6300PSB
  * [please add more!]

Tested with python 2.7 on mac/linux and works fine, your mileage may vary with windows, patches welcome.

### Likely supports

All devices with firmware major version 4, product name "webOSTV 2.0"

## Available Commands
    scan
    auth <Hostname/IP> <name>
    audioStatus
    audioVolume
    closeApp <appid>
    getTVChannel
    input3DOff
    input3DOn
    inputChannelDown
    inputChannelUp
    inputMediaFastForward
    inputMediaPause
    inputMediaPlay
    inputMediaRewind
    inputMediaStop
    listApps
    listChannels
    listInputs
    listServices
    mute <muted>
    notification <message>
    nofificationWithIcon <message> <image_url>
    off
    on
    openAppWithPayload <payload>
    openBrowserAt <url>
    openYoutubeId <videoid>
    openYoutubeURL <url>
    setInput <input_id>
    setTVChannel <channel>
    setVolume <level>
    startApp <appid>
    swInfo
    volumeDown
    volumeUp

## Install

Requires wakeonlan, websocket for python and iproute2

    python -m venv lgtv-venv
    source lgtv-venv/bin/activate
    pip install git+https://github.com/klattimer/LGWebOSRemote

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

## Caveats

You need to auth with the TV before being able to use the on command as it requires the mac address.

## Bugs

I couldn't test youtube because it seems the app isn't installed and not available to download right now
maybe they're updating it?

# LGWebOSRemote
Command line webOS remote for LGTVs

## Available Commands
    scan
    auth                  Hostname/IP     Authenticate and exit, creates initial config ~/.lgtv.json
    audioStatus           
    audioVolume           
    closeApp              appid
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
    mute                  muted
    notification          message
    off                   
    on                    
    openAppWithPayload    payload
    openBrowserAt         url
    openYoutubeId         videoid
    openYoutubeURL        url
    setInput              input_id
    setTVChannel          channel
    setVolume             level
    startApp              appid
    swInfo                
    volumeDown            
    volumeUp

## Install

Requires wakeonlan, websocket for python from here git+https://github.com/klattimer/WebSocket-for-Python.git#egg=ws4py

There's a requirements.txt included

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

The TV doesn't respond when an Origin header (any origin header) is included, so I upstreamed
a patch to handle it but waiting on the pull request https://github.com/Lawouach/WebSocket-for-Python/pull/217.

## Example usage

    $ python lgtv.py on
    $ python lgtv.py off
    $ python lgtv.py openYoutubeURL https://www.youtube.com/watch?v=dQw4w9WgXcQ

## Caveats

You need to auth with the TV before being able to use the on command as it requires the mac address.

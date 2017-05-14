# LGWebOSRemote
Command line webOS remote for LGTVs

## Available Commands
scan
auth                  Authenticate and exit, creates initial config ~/.lgtv.json
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

## Example usage 

  python lgtv.py on
  python lgtv.py off 
  python lgtv.py openYoutubeURL https://www.youtube.com/watch?v=dQw4w9WgXcQ
  
## Caveats 

You need to auth with the TV before being able to use the on command as it requires the mac address.

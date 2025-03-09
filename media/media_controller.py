from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard
import math

class MediaController:
    def __init__(self, speak_callback):
        self.speak_callback = speak_callback
        self.setup_audio()
        
    def setup_audio(self):
        """Initialize audio controls"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"Error setting up audio: {str(e)}")
            self.volume = None
            
    def set_volume(self, level):
        """Set system volume (0-100)"""
        try:
            if self.volume:
                # Convert to decibels (pycaw uses -65.25 to 0.0)
                db = -65.25 * (1.0 - (level / 100.0))
                self.volume.SetMasterVolumeLevel(db, None)
                return True
        except Exception as e:
            print(f"Error setting volume: {str(e)}")
        return False
        
    def mute_unmute(self):
        """Toggle mute state"""
        try:
            if self.volume:
                is_muted = self.volume.GetMute()
                self.volume.SetMute(not is_muted, None)
                return not is_muted
        except Exception as e:
            print(f"Error toggling mute: {str(e)}")
        return None
        
    def get_volume(self):
        """Get current volume level (0-100)"""
        try:
            if self.volume:
                current_vol = self.volume.GetMasterVolumeLevelScalar()
                return math.floor(current_vol * 100)
        except Exception as e:
            print(f"Error getting volume: {str(e)}")
        return None
        
    def media_play_pause(self):
        """Toggle media play/pause"""
        try:
            keyboard.send('play/pause media')
            return True
        except Exception as e:
            print(f"Error with media control: {str(e)}")
            return False
            
    def media_next(self):
        """Next track"""
        try:
            keyboard.send('next track')
            return True
        except Exception as e:
            print(f"Error with media control: {str(e)}")
            return False
            
    def media_previous(self):
        """Previous track"""
        try:
            keyboard.send('previous track')
            return True
        except Exception as e:
            print(f"Error with media control: {str(e)}")
            return False

from speech.voice_handler import VoiceHandler
from monitoring.system_monitor import SystemMonitor
from translation.translator import TranslationHandler
from navigation.trip_planner import TripPlanner
from weather.weather_service import WeatherService
from media.media_controller import MediaController
from utils.system_utils import get_system_info
import datetime
import re
import time
import threading

class Assistant:
    def __init__(self):
        print("Initializing AI Assistant...")
        self.voice = VoiceHandler()
        self.system_monitor = SystemMonitor(self.voice.speak)
        self.translator = TranslationHandler(self.voice.speak)
        self.navigator = TripPlanner(self.voice.speak)
        self.weather = WeatherService(self.voice.speak)
        self.media = MediaController(self.voice.speak)
        self._running = True
        print("Initialization complete!")

    def wish_me(self):
        """Greet the user based on time of day"""
        hour = datetime.datetime.now().hour
        greeting = "Good morning" if 4 <= hour < 12 else "Good afternoon" if 12 <= hour < 18 else "Good evening"
        self.voice.speak(f"{greeting}! I am your AI assistant. How can I help you?")
        
    def process_command(self, query):
        """Process a single voice command"""
        if query == "none":
            return True
            
        print(f"\nCommand received: {query}")
        
        try:
            # Exit commands
            if 'exit' in query or 'quit' in query or 'bye' in query:
                self.voice.speak("Goodbye! Have a great day!")
                self._running = False
                return False
                
            # Time command
            elif 'time' in query:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                response = f"The current time is {current_time}"
                self.voice.speak(response)
                return True
                
            # System monitoring commands
            elif 'system status' in query or 'device status' in query:
                try:
                    system_info = get_system_info()
                    
                    # Print to console
                    print("\n=== System Status ===")
                    print(f"CPU Usage: {system_info['cpu_percent']}%")
                    print(f"Memory Usage: {system_info['memory_percent']}%")
                    print(f"Disk Space Free: {system_info['free_disk']}")
                    
                    # Speak each part with a small pause
                    self.voice.speak(f"CPU usage is {system_info['cpu_percent']} percent")
                    time.sleep(0.5)
                    
                    if system_info['memory_percent'] > 80:
                        self.voice.speak(f"Warning: Memory usage is high at {system_info['memory_percent']} percent")
                    else:
                        self.voice.speak(f"Memory usage is {system_info['memory_percent']} percent")
                    time.sleep(0.5)
                    
                    if system_info['disk_percent'] > 90:
                        self.voice.speak(f"Warning: You only have {system_info['free_disk']} of free disk space")
                    else:
                        self.voice.speak(f"You have {system_info['free_disk']} of free disk space")
                        
                except Exception as e:
                    print(f"Error getting system status: {str(e)}")
                    self.voice.speak("Sorry, I couldn't get the system status")
                return True
                
            # Basic commands
            elif query == 'hello':
                self.voice.speak("Hello! How can I help you today?")
                
            elif 'how are you' in query:
                self.voice.speak("I'm doing well, thank you for asking!")
                
            elif 'your name' in query:
                self.voice.speak("I am your AI Assistant, designed to help you with various tasks.")
                
            # System monitoring commands
            elif 'system status' in query or 'device status' in query:
                self.voice.speak("Checking system status...")
                system_info = get_system_info()
                
                print("\n=== System Status ===")
                print(f"CPU Usage: {system_info['cpu_percent']}%")
                print(f"Memory Usage: {system_info['memory_percent']}%")
                print(f"Disk Space Free: {system_info['free_disk']}")
                
                response = f"CPU usage is {system_info['cpu_percent']} percent. "
                if system_info['memory_percent'] > 80:
                    response += f"Warning: Memory usage is high at {system_info['memory_percent']} percent. "
                else:
                    response += f"Memory usage is {system_info['memory_percent']} percent. "
                
                if system_info['disk_percent'] > 90:
                    response += f"Warning: You only have {system_info['free_disk']} of free disk space."
                else:
                    response += f"You have {system_info['free_disk']} of free disk space."
                
                self.voice.speak(response)
                
            elif any(x in query for x in ['battery', 'power']):
                battery_info = self.system_monitor.get_battery_info()
                if isinstance(battery_info, dict):
                    print("\n=== Battery Status ===")
                    print(f"Battery Level: {battery_info['percent']}%")
                    print(f"Power Status: {'Plugged In' if battery_info['power_plugged'] else 'On Battery'}")
                    
                    self.voice.speak(f"Battery is at {battery_info['percent']} percent")
                    if not battery_info['power_plugged'] and battery_info['percent'] < 20:
                        self.voice.speak("Warning: Battery is low, please connect to power")
                else:
                    self.voice.speak("Sorry, I couldn't get battery information")

            elif 'network' in query or 'internet' in query:
                net_info = self.system_monitor.get_network_info()
                if isinstance(net_info, dict):
                    print("\n=== Network Status ===")
                    print(f"Data Sent: {net_info['bytes_sent']}")
                    print(f"Data Received: {net_info['bytes_received']}")
                    print("\nActive Interfaces:")
                    for interface in net_info['active_interfaces']:
                        print(f"- {interface}")
                    
                    self.voice.speak(f"Network is active. You have sent {net_info['bytes_sent']} and received {net_info['bytes_received']} of data")
                else:
                    self.voice.speak("Sorry, I couldn't get network information")

            elif 'process' in query or 'running' in query or 'program' in query:
                self.voice.speak("Checking running processes")
                processes = self.system_monitor.get_running_processes()
                
                print("\n=== Top CPU-Intensive Processes ===")
                for proc in processes[:5]:
                    if proc['name']:  # Only show processes with names
                        print(f"{proc['name']:<30} CPU: {proc['cpu_percent']:>5.1f}%    RAM: {proc['memory_percent']:>5.1f}%")
                
                self.voice.speak(f"I've displayed the top {len(processes[:5])} CPU-intensive processes")

            # Translation commands
            elif query.startswith('translate'):
                # Remove 'translate' from the start
                text = query.replace('translate', '', 1).strip()
                
                # Check for 'to' or 'in' separator
                for separator in [' to ', ' in ']:
                    if separator in text:
                        parts = text.split(separator)
                        if len(parts) == 2:
                            text_to_translate = parts[0].strip()
                            target_lang = parts[1].strip()
                            
                            if text_to_translate and target_lang:
                                print(f"\nTranslating: '{text_to_translate}' to {target_lang}")
                                translation = self.translator.translate_text(text_to_translate, to_lang=target_lang)
                                
                                if translation:
                                    print(f"Translation: {translation}")
                                    self.voice.speak(f"'{text_to_translate}' in {target_lang} is:")
                                    if self.translator.speak_in_language(translation, target_lang):
                                        print(f"Spoken translation in {target_lang}")
                                    else:
                                        self.voice.speak(translation)
                                    return True
                                
                self.voice.speak("Please say: translate [your text] to [language]")
                print("\nExamples:")
                print("- translate hello to spanish")
                print("- translate good morning to french")
                return False

            # Navigation commands
            elif any(x in query for x in ['direction', 'route', 'navigate']):
                if 'directions' in query or 'route' in query or 'navigate' in query:
                    locations = self.navigator.parse_location_input(query)
                    if locations:
                        self.voice.speak(f"Getting directions from {locations['current_location']} to {locations['destination']}")
                        print(f"\n=== Navigation ===")
                        print(f"From: {locations['current_location']}")
                        print(f"To: {locations['destination']}")
                        
                        directions = self.navigator.get_directions(
                            locations['current_location'],
                            locations['destination']
                        )
                        
                        if directions:
                            print("\nDirections:")
                            print(directions)
                            self.voice.speak("I've found the directions and displayed them on screen")
                            return True
                        else:
                            self.voice.speak("Sorry, I couldn't get directions for that route")
                    else:
                        self.voice.speak("Please specify the start and destination locations")
                        print("\nExamples:")
                        print("- get directions from New York to Boston")
                        print("- show route from London to Paris")
                        print("- navigate from home to airport")
                return False

            # Weather commands
            elif 'weather' in query:
                # Extract city name
                city_match = None
                patterns = [
                    r'weather (?:in|at|for) (.+)',
                    r'weather of (.+)',
                    r'(.+) weather'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        city_match = match.group(1).strip()
                        break
                
                if not city_match:
                    self.voice.speak("Please specify a city. For example, 'weather in London' or 'Mumbai weather'")
                    return False
                    
                weather_info = self.weather.get_weather(city_match)
                if weather_info:
                    print(f"\n{weather_info}")
                    self.voice.speak(f"Here's the weather for {city_match}")
                    return True
                else:
                    self.voice.speak(f"Sorry, I couldn't get the weather for {city_match}")
                    return False

            # Media control commands
            elif any(x in query for x in ['volume', 'mute', 'unmute', 'play', 'pause', 'next', 'previous']):
                if 'volume' in query:
                    # Extract volume level if specified
                    level_match = re.search(r'(?:set |change |make |turn )?volume (?:to |at )?(\d+)', query)
                    if level_match:
                        level = int(level_match.group(1))
                        if 0 <= level <= 100:
                            if self.media.set_volume(level):
                                self.voice.speak(f"Volume set to {level} percent")
                                return True
                            else:
                                self.voice.speak("Sorry, I couldn't change the volume")
                        else:
                            self.voice.speak("Please specify a volume level between 0 and 100")
                    else:
                        # Get current volume
                        current_vol = self.media.get_volume()
                        if current_vol is not None:
                            self.voice.speak(f"Current volume is {current_vol} percent")
                            return True
                        
                elif 'mute' in query or 'unmute' in query:
                    result = self.media.mute_unmute()
                    if result is not None:
                        self.voice.speak("Audio unmuted" if result else "Audio muted")
                        return True
                    else:
                        self.voice.speak("Sorry, I couldn't control the audio")
                        
                elif any(x in query for x in ['play', 'pause', 'resume']):
                    if self.media.media_play_pause():
                        self.voice.speak("Toggled media playback")
                        return True
                    else:
                        self.voice.speak("Sorry, I couldn't control media playback")
                        
                elif 'next' in query:
                    if self.media.media_next():
                        self.voice.speak("Playing next track")
                        return True
                    else:
                        self.voice.speak("Sorry, I couldn't play next track")
                        
                elif 'previous' in query or 'last' in query:
                    if self.media.media_previous():
                        self.voice.speak("Playing previous track")
                        return True
                    else:
                        self.voice.speak("Sorry, I couldn't play previous track")
                        
                return False

            elif 'help' in query:
                print("\n=== Available Commands ===")
                print("1. System Commands:")
                print("   - system status")
                print("   - battery status")
                print("   - network status")
                print("   - show running processes")
                
                print("\n2. Translation Commands:")
                print("   - translate [text] to [language]")
                print("   - translate [text] in [language]")
                print("   - what languages can you translate")
                
                print("\n3. Navigation Commands:")
                print("   - get directions from [place] to [place]")
                print("   - show route from [place] to [place]")
                print("   - navigate from [place] to [place]")
                
                print("\n4. Weather Commands:")
                print("   - weather in [city]")
                print("   - what's the weather in [city]")
                print("   - [city] weather")
                
                print("\n5. Media Control Commands:")
                print("   - set volume to [0-100]")
                print("   - mute/unmute")
                print("   - play/pause")
                print("   - next track")
                print("   - previous track")
                
                self.voice.speak("I've displayed a list of available commands on screen")

            else:
                self.voice.speak("Sorry, I didn't understand that command. Please try again.")
                
        except Exception as e:
            print(f"Error processing command: {str(e)}")
            self.voice.speak("Sorry, I encountered an error. Please try again.")
            
        return True

    def run(self):
        """Main loop of the assistant"""
        try:
            self.wish_me()
            self.system_monitor.start_monitoring()
            
            while self._running:
                query = self.voice.take_command().lower().strip()
                if not self.process_command(query):
                    break
                    
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            self.voice.speak("Sorry, I encountered an error. Please restart me.")
            
        finally:
            self.system_monitor.stop_monitoring()
            
if __name__ == "__main__":
    assistant = Assistant()
    assistant.run()

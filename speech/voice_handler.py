import speech_recognition as sr
import win32com.client
import time

class VoiceHandler:
    def __init__(self):
        print("Initializing voice system...")
        try:
            # Initialize Windows SAPI for text-to-speech
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.5
            
            print("Voice system initialized!")
            
        except Exception as e:
            print(f"Error initializing voice system: {str(e)}")
            raise

    def speak(self, text):
        """Convert text to speech using Windows SAPI"""
        if not text:
            return
            
        try:
            # Print what the assistant is saying
            print(f"\nAssistant: {text}")
            
            # Speak the text
            self.speaker.Speak(text)
                
        except Exception as e:
            print(f"Speech Error: {str(e)}")
            try:
                # Try to recover by reinitializing
                self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
                self.speaker.Speak(text)
            except:
                print("Failed to recover speech system")

    def take_command(self):
        """Take microphone input and return string output"""
        with sr.Microphone() as source:
            print("\nListening...")
            try:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Get audio input
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Recognizing...")
                
                # Convert speech to text
                query = self.recognizer.recognize_google(audio, language='en-in')
                if query:
                    print(f"You said: {query}")
                    return query.lower()
                    
            except sr.WaitTimeoutError:
                print("No speech detected")
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that")
            except sr.RequestError:
                print("Sorry, there was an error with the speech recognition service")
            except Exception as e:
                print(f"Error: {str(e)}")
            
            return "none"

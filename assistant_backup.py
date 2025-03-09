import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
import datetime
import wikipedia #pip install wikipedia
import webbrowser
import os
import smtplib
import re
import geocoder
import requests
import cv2
import numpy as np
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pywhatkit  # for playing YouTube songs
from googletrans import Translator, LANGUAGES  # for translation
from gtts import gTTS  # for multilingual text-to-speech
import playsound  # for playing the generated speech
import uuid  # for generating unique filenames
import openai
from datetime import datetime
import psutil
import wmi
import cpuinfo
import GPUtil
import platform
import threading
import time

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[0].id)

# Initialize OpenAI with Deepseek API key
openai.api_key = "sk-307675855e854869bb33ed3a48238501"
openai.api_base = "https://api.deepseek.com/v1"  # Use Deepseek's API endpoint

def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!")  

    speak("I am Jarvis Sir. Please tell me how may I help you")       

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@gmail.com', 'your-password')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()
    
def trip():
    engine = pyttsx3.init('sapi5')
    engine.say("Where do you want to go")
    engine.runAndWait()
    rate = 130
    engine.setProperty('rate', rate)
    volume = 0.9
    engine.setProperty('volume', volume)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    r = sr.Recognizer()
    mic = sr.Microphone()
    

    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Please give input as from your current location to destination ")
        print("Please state your current location and destination:")
        response = r.listen(source)

    try:
        user_input = r.recognize_google(response)
        print("User input:", user_input)
    except sr.UnknownValueError:
        print("Unable to recognize speech")
        return
    except sr.RequestError as e:
        print("Error:", e)
        return

    location_regex = r'from\s([\w\s]+)\sto'
    destination_regex = r'to\s([\w\s]+)'

    location_match = re.search(location_regex, user_input, re.IGNORECASE)
    destination_match = re.search(destination_regex, user_input, re.IGNORECASE)

    if location_match and destination_match:
        current_location = location_match.group(1).strip()
        destination = destination_match.group(1).strip()
        print("Current location:", current_location)
        print("Destination:", destination)
    else:
        print("Unable to extract location and destination from user input")
        return

    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the Chrome WebDriver with the updated method
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Construct the Google Maps URL
        url = f"https://www.google.com/maps/dir/{current_location}/{destination}"
        driver.get(url)
        
        # Wait for the directions to load
        wait = WebDriverWait(driver, 10)
        directions = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-directions-trip-description")))
        
        # Get and print the directions
        print("\nDirections:")
        print(directions.text)
        
    except Exception as e:
        print(f"An error occurred while getting directions: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

def get_language_code(language_name):
    # Convert full language name to language code
    language_name = language_name.lower()
    for code, name in LANGUAGES.items():
        if name.lower() == language_name:
            return code
    return None

def speak_in_language(text, lang_code):
    try:
        # Generate a unique filename for this speech
        filename = f"speech_{str(uuid.uuid4())}.mp3"
        # Create gTTS object and save to file
        tts = gTTS(text=text, lang=lang_code)
        tts.save(filename)
        # Play the file
        playsound.playsound(filename)
        # Clean up the file
        os.remove(filename)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        speak("I encountered an error while trying to speak the translation.")

def translate_text():
    translator = Translator()
    
    speak("What would you like me to translate?")
    text_to_translate = takeCommand()
    if text_to_translate == "None":
        speak("I couldn't catch that. Could you please repeat?")
        return
    
    speak("Which language is this text in? If you're not sure, just say 'auto detect'")
    from_lang = takeCommand().lower()
    if from_lang == "None":
        speak("I couldn't understand the language. Let's try again.")
        return
    
    if 'auto' in from_lang or 'detect' in from_lang:
        from_lang = 'auto'
    else:
        from_lang = get_language_code(from_lang)
        if not from_lang:
            speak("I don't recognize that language. Let's try again.")
            return
    
    speak("What language should I translate it to?")
    to_lang = takeCommand().lower()
    if to_lang == "None":
        speak("I couldn't understand the target language. Let's try again.")
        return
    
    to_lang = get_language_code(to_lang)
    if not to_lang:
        speak("I don't recognize that language. Let's try again.")
        return
    
    try:
        speak("Let me translate that for you...")
        translation = translator.translate(text_to_translate, src=from_lang, dest=to_lang)
        print(f"Original text: {text_to_translate}")
        print(f"Translation: {translation.text}")
        
        # First announce in English
        speak(f"Here's the translation in {LANGUAGES[to_lang]}")
        # Then speak the translation in the target language
        speak_in_language(translation.text, to_lang)
        
        speak("Would you like me to translate something else?")
        response = takeCommand().lower()
        if 'yes' in response or 'yeah' in response:
            translate_text()
    except Exception as e:
        speak("I encountered an error while translating. Please try again.")

def create_file(file_type, content, filename=None):
    """Create a file with the specified content and type"""
    if filename is None:
        # Generate a filename with timestamp if none provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.{file_type}"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        speak(f"File {filename} has been created successfully")
        return filename
    except Exception as e:
        speak(f"Sorry, I couldn't create the file. Error: {str(e)}")
        return None

def ai_chat(prompt):
    """Have a conversation with Deepseek AI"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def generate_code(prompt):
    """Generate code using Deepseek AI"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-coder",
            messages=[{"role": "user", "content": f"Generate code for: {prompt}"}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I couldn't generate the code: {str(e)}"

def summarize_text(text):
    """Summarize text using Deepseek AI"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"Please summarize this text: {text}"}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I couldn't summarize the text: {str(e)}"

def get_size(bytes):
    """
    Convert bytes to human readable format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def get_system_info():
    """Get detailed system information"""
    try:
        info = {}
        # CPU information
        info['cpu_percent'] = psutil.cpu_percent(interval=1)
        info['cpu_cores'] = psutil.cpu_count()
        info['cpu_freq'] = psutil.cpu_freq().current
        
        # Memory information
        memory = psutil.virtual_memory()
        info['total_memory'] = get_size(memory.total)
        info['available_memory'] = get_size(memory.available)
        info['memory_percent'] = memory.percent
        
        # Disk information
        disk = psutil.disk_usage('/')
        info['total_disk'] = get_size(disk.total)
        info['free_disk'] = get_size(disk.free)
        info['disk_percent'] = disk.percent
        
        # Battery information if available
        battery = psutil.sensors_battery()
        if battery:
            info['battery_percent'] = battery.percent
            info['power_plugged'] = battery.power_plugged
            
        # Network information
        network = psutil.net_io_counters()
        info['bytes_sent'] = get_size(network.bytes_sent)
        info['bytes_received'] = get_size(network.bytes_recv)
        
        return info
    except Exception as e:
        return f"Error getting system info: {str(e)}"

def get_running_processes(limit=10):
    """Get information about running processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU usage and get top processes
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

def analyze_system_health():
    """Analyze system health and get AI recommendations"""
    system_info = get_system_info()
    processes = get_running_processes()
    
    # Create a detailed system report for AI analysis
    system_report = f"""
    System Health Report:
    CPU Usage: {system_info['cpu_percent']}%
    Memory Usage: {system_info['memory_percent']}%
    Disk Usage: {system_info['disk_percent']}%
    Available Memory: {system_info['available_memory']}
    Free Disk Space: {system_info['free_disk']}
    
    Top CPU-Intensive Processes:
    {', '.join([f"{p['name']} ({p['cpu_percent']}%)" for p in processes[:5]])}
    """
    
    try:
        # Get AI recommendations based on system status
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[{
                "role": "user", 
                "content": f"Analyze this system health report and provide specific recommendations for optimization and maintenance. If any metrics are concerning, highlight them: {system_report}"
            }],
            temperature=0.7,
            max_tokens=500
        )
        return system_report, response.choices[0].message.content
    except Exception as e:
        return system_report, f"Error getting AI recommendations: {str(e)}"

def monitor_performance_metrics():
    """Monitor real-time performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = f"""
        Current Performance Metrics:
        CPU Usage: {cpu_percent}%
        Memory Usage: {memory.percent}%
        Disk Usage: {disk.percent}%
        """
        return metrics
    except Exception as e:
        return f"Error monitoring performance: {str(e)}"

def get_battery_info():
    """Get detailed battery information"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                'percent': battery.percent,
                'power_plugged': battery.power_plugged,
                'time_left': str(datetime.timedelta(seconds=battery.secsleft)) if battery.secsleft > 0 else "Unknown"
            }
        return None
    except Exception as e:
        return f"Error getting battery info: {str(e)}"

def get_network_info():
    """Get detailed network information"""
    try:
        info = {}
        # Get network interfaces
        interfaces = psutil.net_if_stats()
        active_interfaces = []
        
        for interface, stats in interfaces.items():
            if stats.isup:
                active_interfaces.append(interface)
                
        # Get network usage
        net_io = psutil.net_io_counters()
        info['active_interfaces'] = active_interfaces
        info['bytes_sent'] = get_size(net_io.bytes_sent)
        info['bytes_received'] = get_size(net_io.bytes_recv)
        info['packets_sent'] = net_io.packets_sent
        info['packets_received'] = net_io.packets_recv
        
        return info
    except Exception as e:
        return f"Error getting network info: {str(e)}"

def monitor_system_continuously(interval=5):
    """Monitor system continuously and alert if thresholds are exceeded"""
    try:
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check for high resource usage
            alerts = []
            if cpu_percent > 80:
                alerts.append(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 85:
                alerts.append(f"High memory usage: {memory.percent}%")
            if disk.percent > 90:
                alerts.append(f"Low disk space: {get_size(disk.free)} remaining")
                
            if alerts:
                print("\nSystem Alerts:")
                for alert in alerts:
                    print(f"⚠️ {alert}")
                    speak(f"Alert: {alert}")
            
            time.sleep(interval)
    except Exception as e:
        print(f"Error in continuous monitoring: {str(e)}")

def get_gpu_info():
    """Get GPU information if available"""
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_info = []
            for gpu in gpus:
                info = {
                    'name': gpu.name,
                    'load': f"{gpu.load*100}%",
                    'memory_used': f"{gpu.memoryUsed}MB",
                    'memory_total': f"{gpu.memoryTotal}MB",
                    'temperature': f"{gpu.temperature}°C"
                }
                gpu_info.append(info)
            return gpu_info
        return None
    except Exception as e:
        return f"Error getting GPU info: {str(e)}"

def analyze_startup_programs():
    """Analyze startup programs and their impact"""
    try:
        w = wmi.WMI()
        startup_programs = w.Win32_StartupCommand()
        
        startup_info = []
        for program in startup_programs:
            startup_info.append({
                'name': program.Name,
                'command': program.Command,
                'location': program.Location
            })
            
        # Get AI recommendations for startup optimization
        if startup_info:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": f"Analyze these startup programs and suggest which ones might be unnecessary or impacting system performance: {startup_info}"
                }],
                temperature=0.7,
                max_tokens=500
            )
            return startup_info, response.choices[0].message.content
        return startup_info, "No startup programs found"
    except Exception as e:
        return None, f"Error analyzing startup programs: {str(e)}"

if __name__ == "__main__":
    # Start system monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_system_continuously, daemon=True)
    monitor_thread.start()
    
    wishMe()
    while True:
        query = takeCommand().lower()
        
        # Logic for executing tasks based on query
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except Exception as e:
                speak("Sorry, I couldn't find that information on Wikipedia")
                
        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'play' in query and 'youtube' in query:
            try:
                song = query.replace('play', '').replace('on youtube', '').strip()
                speak(f'Playing {song} on YouTube')
                pywhatkit.playonyt(song)
            except Exception as e:
                speak("Sorry, I couldn't play that video")

        elif 'translate' in query:
            translate_text()
            
        elif 'directions' in query or 'navigate' in query:
            trip()

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")    
            speak(f"Sir, the time is {strTime}")

        # New Deepseek AI and file creation commands
        elif 'create file' in query:
            speak("What type of file would you like to create? Text, HTML, or Python?")
            file_type = takeCommand().lower()
            
            if 'text' in file_type:
                ext = 'txt'
            elif 'html' in file_type:
                ext = 'html'
            elif 'python' in file_type:
                ext = 'py'
            else:
                speak("Sorry, I don't support that file type")
                continue
                
            speak("What should the file contain?")
            content = takeCommand()
            if content != "None":
                create_file(ext, content)
            else:
                speak("Sorry, I couldn't understand the content")

        elif 'chat with ai' in query:
            speak("What would you like to discuss?")
            prompt = takeCommand()
            if prompt != "None":
                response = ai_chat(prompt)
                print(response)
                speak(response)

        elif 'generate code' in query:
            speak("What kind of code would you like me to generate?")
            prompt = takeCommand()
            if prompt != "None":
                code = generate_code(prompt)
                print(code)
                speak("I've generated the code. Would you like me to save it to a file?")
                save_response = takeCommand().lower()
                if 'yes' in save_response:
                    create_file('py', code)

        elif 'summarize' in query:
            speak("What text would you like me to summarize?")
            text = takeCommand()
            if text != "None":
                summary = summarize_text(text)
                print(summary)
                speak(summary)

        elif 'system status' in query or 'device status' in query:
            speak("Checking system status and health...")
            system_report, ai_recommendations = analyze_system_health()
            
            # Add GPU information if available
            gpu_info = get_gpu_info()
            if isinstance(gpu_info, list):
                print("\nGPU Information:")
                for gpu in gpu_info:
                    print(f"\nGPU: {gpu['name']}")
                    print(f"Load: {gpu['load']}")
                    print(f"Memory: {gpu['memory_used']}/{gpu['memory_total']}")
                    print(f"Temperature: {gpu['temperature']}")
            
            print("\nSystem Report:")
            print(system_report)
            speak("Here's what I found about your system")
            print("\nAI Recommendations:")
            print(ai_recommendations)
            speak("Based on my analysis, " + ai_recommendations)

        elif 'network status' in query or 'check internet' in query:
            speak("Checking network status")
            net_info = get_network_info()
            print("\nNetwork Information:")
            for key, value in net_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            speak("I've displayed the network information on screen")

        elif 'battery status' in query or 'power status' in query:
            battery_info = get_battery_info()
            if isinstance(battery_info, dict):
                print("\nBattery Information:")
                print(f"Battery Level: {battery_info['percent']}%")
                print(f"Power Plugged: {'Yes' if battery_info['power_plugged'] else 'No'}")
                print(f"Time Left: {battery_info['time_left']}")
                speak(f"Battery is at {battery_info['percent']} percent")
                if not battery_info['power_plugged'] and battery_info['percent'] < 20:
                    speak("Warning: Battery is low, please connect to power")
            else:
                speak("Sorry, I couldn't get battery information")

        elif 'startup programs' in query or 'check startup' in query:
            speak("Analyzing startup programs")
            programs, recommendations = analyze_startup_programs()
            if programs:
                print("\nStartup Programs:")
                for program in programs:
                    print(f"\nName: {program['name']}")
                    print(f"Command: {program['command']}")
                    print(f"Location: {program['location']}")
                print("\nRecommendations:")
                print(recommendations)
                speak("I've found some startup programs that might be affecting your system performance")
            else:
                speak("I couldn't retrieve startup program information")

        elif 'monitor system' in query:
            speak("Starting continuous system monitoring. I'll alert you if any issues are detected")
            print("Continuous monitoring is active. You'll be alerted of any issues.")
            # The monitoring is already running in background thread

        elif 'exit' in query or 'quit' in query:
            speak("Goodbye!")
            break
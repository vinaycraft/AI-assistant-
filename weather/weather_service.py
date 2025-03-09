import requests
import json
from datetime import datetime

class WeatherService:
    def __init__(self, speak_callback):
        self.speak_callback = speak_callback
        self.api_key = "YOUR_API_KEY"  # Get from OpenWeatherMap
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city):
        """Get current weather for a city"""
        try:
            # For demo, return mock data since API key isn't set
            return self.get_mock_weather(city)
            
            # Uncomment below for real API usage
            # params = {
            #     'q': city,
            #     'appid': self.api_key,
            #     'units': 'metric'
            # }
            # response = requests.get(self.base_url, params=params)
            # data = response.json()
            # return self.format_weather_data(data)
            
        except Exception as e:
            print(f"Error getting weather: {str(e)}")
            return None
            
    def get_mock_weather(self, city):
        """Return mock weather data for demo"""
        mock_data = {
            'name': city,
            'main': {
                'temp': 25,
                'feels_like': 26,
                'humidity': 65,
                'pressure': 1012
            },
            'weather': [{'description': 'partly cloudy'}],
            'wind': {'speed': 12}
        }
        return self.format_weather_data(mock_data)
            
    def format_weather_data(self, data):
        """Format weather data into readable string"""
        try:
            weather_info = f"""
=== Weather in {data['name']} ===
Temperature: {data['main']['temp']}°C
Feels like: {data['main']['feels_like']}°C
Conditions: {data['weather'][0]['description']}
Humidity: {data['main']['humidity']}%
Wind Speed: {data['wind']['speed']} km/h
            """
            return weather_info.strip()
        except:
            return None

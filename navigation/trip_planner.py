import re
from urllib.parse import quote
import webbrowser

class TripPlanner:
    def __init__(self, speak_callback):
        self.speak_callback = speak_callback

    def parse_location_input(self, user_input):
        """Extract location and destination from user input"""
        location_regex = r'from\s([\w\s,]+)\sto'
        destination_regex = r'to\s([\w\s,]+)(?:\s|$)'

        location_match = re.search(location_regex, user_input, re.IGNORECASE)
        destination_match = re.search(destination_regex, user_input, re.IGNORECASE)

        if location_match and destination_match:
            return {
                'current_location': location_match.group(1).strip(),
                'destination': destination_match.group(1).strip()
            }
        return None

    def get_directions(self, current_location, destination):
        """Open Google Maps in the default browser"""
        try:
            # Encode locations for URL
            origin_encoded = quote(current_location)
            destination_encoded = quote(destination)
            
            # Create Google Maps URL
            maps_url = f"https://www.google.com/maps/dir/{origin_encoded}/{destination_encoded}"
            
            # Open URL in default browser
            webbrowser.open(maps_url)
            
            return f"I've opened Google Maps with directions from {current_location} to {destination}"
        except Exception as e:
            print(f"Error opening maps: {str(e)}")
            return None

    def plan_trip(self, user_input):
        """Main method to handle trip planning"""
        locations = self.parse_location_input(user_input)
        if not locations:
            self.speak_callback("I couldn't understand the locations. Please specify them as 'from [location] to [destination]'")
            return False

        self.speak_callback(f"Getting directions from {locations['current_location']} to {locations['destination']}")
        
        result = self.get_directions(locations['current_location'], locations['destination'])
        if result:
            print("\n=== Navigation ===")
            print(f"From: {locations['current_location']}")
            print(f"To: {locations['destination']}")
            print(f"\n{result}")
            self.speak_callback("I've opened Google Maps in your browser")
            return True
        else:
            self.speak_callback("Sorry, I couldn't open the directions at this time")
            return False

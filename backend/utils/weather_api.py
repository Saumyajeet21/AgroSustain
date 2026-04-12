import os
import requests
from dotenv import load_dotenv

# Let's load the secrets from the .env file!
load_dotenv()

def fetch_live_weather(lat: float, lon: float):
    """
    Fetches real-time temperature, humidity, and rainfall from OpenWeatherMap API
    """
    # Grab the key from the .env file
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key or api_key == "your_openweather_api_key_here":
        return {"success": False, "error": "The OpenWeather API key is missing or you forgot to save the .env file!"}
        
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric" # Gives us Celsius
    }
    
    print(f"[Weather] Pinging OpenWeatherMap for coordinates: {lat}, {lon}...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            
            # If no rain reported, default to 0.0
            rainfall = 0.0
            if 'rain' in data and '1h' in data['rain']:
                rainfall = data['rain']['1h']
                
            return {
                "success": True,
                "temperature": temp,
                "humidity": humidity,
                "rainfall": rainfall,
                "location": data.get('name', 'Unknown')
            }
        
        elif response.status_code == 401:
            return {"success": False, "error": "Unauthorized! Your API key might be invalid or hasn't activated yet (takes ~15 mins after creating it)."}
        else:
            return {"success": False, "error": f"API Error {response.status_code}: {response.json().get('message', 'Unknown')}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection Failed: {str(e)}"}

# --- Let's run a test if you execute this file directly ---
if __name__ == "__main__":
    # Test for Delhi
    test_lat = 28.6139
    test_lon = 77.2090
    print("Testing OpenWeatherMap API connection...")
    result = fetch_live_weather(test_lat, test_lon)
    print("🎯 Result:", result)

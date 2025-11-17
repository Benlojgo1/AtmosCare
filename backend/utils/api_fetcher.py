import requests
import os

BASE_URL = "http://api.weatherapi.com/v1"

# --- fetch current weather ---
def fetch_current_weather(zip_code, api_key):
    """Fetches current weather and air quality for a given zip code."""
    try:
        endpoint = f"{BASE_URL}/current.json?key={api_key}&q={zip_code}&aqi=yes"
        
        response = requests.get(endpoint)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        # ... rest of your data processing logic ...
        data = response.json()
        
        weather_data = {
            "timestamp": data['current']['last_updated_epoch'],
            "temperature": data['current']['temp_c'],
            "humidity": data['current']['humidity'],
            "air_quality_index": data['current']['air_quality']['us-epa-index']
        }
        return weather_data

    except requests.exceptions.RequestException as e:
        print(f"API Error fetching data for {zip_code}: {e}")
        return None
    
if __name__ == '__main__':
    from dotenv import load_dotenv

    # Load the environment variables from the .env file
    load_dotenv()
    
    # Get the API_KEY value inside the main block
    API_KEY_VALUE = os.getenv('WEATHER_API_KEY')
    
    # 3. Choose a test ZIP code (e.g., a major city)
    TEST_ZIP = '78520' # Example: Brownsville, Texas
    
    if API_KEY_VALUE:
        print(f"--- Testing WeatherAPI for ZIP: {TEST_ZIP} ---")
        
        # --- FIX 3: Pass the API_KEY_VALUE to the function ---
        result = fetch_current_weather(TEST_ZIP, API_KEY_VALUE)
        
        # 5. Print the result
        if result:
            import json
            print("Successfully fetched and processed data:")
            print(json.dumps(result, indent=4))
        else:
            print("Test failed or returned None.")
    else:
        print("ERROR: WEATHER_API_KEY not found in environment variables.")
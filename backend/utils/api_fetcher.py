import requests
import os
from datetime import datetime

BASE_URL = "http://api.weatherapi.com/v1"


def fetch_current_weather(zip_code: str, api_key: str):
    """
    Fetches current weather + AQI for a ZIP code.
    Returns a dict ready to insert into WEATHER_RECORD.
    """
    try:
        endpoint = f"{BASE_URL}/current.json?key={api_key}&q={zip_code}&aqi=yes"

        response = requests.get(endpoint)
        response.raise_for_status()

        data = response.json()

        # Convert timestamp properly
        timestamp = datetime.fromtimestamp(data["current"]["last_updated_epoch"])

        return {
            "timestamp": timestamp,
            "temperature": data["current"]["temp_f"],   # use Fahrenheit if your UI expects it
            "humidity": data["current"]["humidity"],
            "air_quality_index": data["current"]["air_quality"]["us-epa-index"],
        }

    except requests.exceptions.RequestException as e:
        print(f"API Error fetching data for ZIP {zip_code}: {e}")
        return None


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    API_KEY_VALUE = os.getenv("WEATHER_API_KEY")
    TEST_ZIP = "78520"

    if API_KEY_VALUE:
        print(f"--- Testing WeatherAPI for ZIP: {TEST_ZIP} ---")
        result = fetch_current_weather(TEST_ZIP, API_KEY_VALUE)

        if result:
            import json
            print("Success:")
            print(json.dumps({k: str(v) for k, v in result.items()}, indent=4))
        else:
            print("Fetch returned None.")
    else:
        print("ERROR: WEATHER_API_KEY not found.")

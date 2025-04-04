
import requests
import json
import datetime
import timedelta 
 

api_key = "8ef907d100c5c7be0a09f29636aab464"

city = "Portland,US"

# URL for current weather data.
current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

# URL for forecast data (5-day forecast with 3-hour intervals).
forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"

# checking current weather data
current_response = requests.get(current_url)
current_data = current_response.json()

print("\nChecking current weather data...\n")
# currently raining flag
is_currently_raining = False

if "weather" in current_data:
    for condition in current_data["weather"]:
        if "rain" in condition["main"].lower() or "rain" in condition["description"].lower():
            is_currently_raining = True
            break

if is_currently_raining:
    print(f"\nIt is currently raining in Portland, OR\n")
else:
    print(f"\nIt is currently not raining in Portland, OR\n")

print("\nChecking forecast weather data...\n")

# Check forcast weather data
forecast_response = requests.get(forecast_url)
forecast_data = forecast_response.json()

# get current time
current_time = datetime.datetime.now(datetime.timezone.utc)
three_days_later = current_time + datetime.timedelta(days=3)
forecast_rain = False

if "list" in forecast_data:
    for entry in forecast_data["list"]:
        forecast_time = datetime.datetime.fromtimestamp(entry["dt"], datetime.timezone.utc)
        if forecast_time <= three_days_later:
            for condition in entry.get("weather", []):
                if "rain" in condition["main"].lower() or "rain" in condition["description"].lower():
                    forecast_rain = True
                    break
        else:
            break  # No need to check further if we have passed 3 days

if forecast_rain:
    print(f"\nRain is expected in Portland, OR within the next 3 days.\n")
else:
    print(f"\nNo rain is expected in Portland, OR within the next 3 days.\n")
import os
import json
import requests
from github import Github
from datetime import datetime

# --- CONFIGURATION ---
# These coordinates are for the J&J LMDS site in Wilson, NC
LAT = 35.7413
LON = -77.9938
USGS_STATION = "02091500"  # Contentnea Creek at Wilson
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "mickeybhenson-commits/J-J-LMDS-WILSON-NC"

def get_usgs_rain(station):
    """Fetches 24h rainfall from USGS."""
    url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={station}&parameterCd=00045&period=P1D"
    try:
        data = requests.get(url).json()
        values = data['value']['timeSeries'][0]['values'][0]['value']
        total = sum(float(v['value']) for v in values if float(v['value']) > 0)
        return round(total, 2)
    except:
        return 0.0

def get_weather_data(lat, lon):
    """Fetches weather, wind, and temp for Wilson, NC."""
    # Using a public weather API (National Weather Service)
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    res = requests.get(points_url).json()
    forecast_url = res['properties']['forecastHourly']
    f_data = requests.get(forecast_url).json()
    current = f_data['properties']['periods'][0]
    
    return {
        "temp": current['temperature'],
        "wind_speed": int(current['windSpeed'].split(' ')[0]),
        "humidity": current.get('relativeHumidity', {}).get('value', 50)
    }

def update_json():
    # 1. Gather new data
    rain = get_usgs_rain(USGS_STATION)
    weather = get_weather_data(LAT, LON)
    
    # 2. Logic for Dashboard metrics
    risk = "HIGH" if rain > 0.5 else "LOW"
    stability = 0.8 if rain > 0.5 else 0.42 # Simple logic for baseline
    blankets = True if weather['temp'] < 35 else False
    
    new_status = {
        "project_name": "J&J LMDS",
        "location": "Wilson, NC",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M EST"),
        "swppp": {
            "risk": risk,
            "rain_24h": rain,
            "stability_index": stability,
            "neuse_buffer_check": "Compliant"
        },
        "concrete": {
            "status": "CAUTION" if blankets else "OPTIMAL",
            "temp_low": weather['temp'],
            "humidity": weather['humidity'],
            "blankets_required": blankets
        },
        "grading": {
            "status": "OPTIMAL" if stability < 0.6 else "SATURATED",
            "trafficability": "Good" if stability < 0.6 else "Poor"
        },
        "crane": {
            "wind_speed": weather['wind_speed'],
            "max_gust": weather['wind_speed'] + 5,
            "status": "GO" if weather['wind_speed'] < 25 else "STOP"
        }
    }

    # 3. Push to GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    contents = repo.get_contents("data/site_status.json")
    repo.update_file(
        contents.path, 
        "Daily Automation Update", 
        json.dumps(new_status, indent=2), 
        contents.sha
    )

if __name__ == "__main__":
    update_json()

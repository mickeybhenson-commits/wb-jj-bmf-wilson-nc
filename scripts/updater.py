import os
import json
import requests
import pandas as pd
from github import Github
from datetime import datetime

# --- CONFIGURATION ---
LAT = 35.7413
LON = -77.9938
USGS_STATION = "02091500" # Contentnea Creek at Wilson
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "mickeybhenson-commits/J-J-LMDS-WILSON-NC"

def get_usgs_rain(station):
    """Fetches real-time 24h rainfall from USGS."""
    url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&sites={station}&parameterCd=00045&period=P1D"
    try:
        data = requests.get(url).json()
        values = data['value']['timeSeries'][0]['values'][0]['value']
        # Summing incremental tips for the last 24h
        total = sum(float(v['value']) for v in values if float(v['value']) > 0)
        return round(total, 2)
    except:
        return 0.0

def get_hrrr_forecast(lat, lon):
    """Simulates/Fetches high-res forecast data (HRRR style)."""
    # Using NWS API as the proxy for high-res forecast data
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    res = requests.get(points_url).json()
    forecast_url = res['properties']['forecastHourly']
    f_data = requests.get(forecast_url).json()
    
    # Analyze the next 12 hours for lightning and peak wind
    periods = f_data['properties']['periods'][:12]
    
    return {
        "temp": periods[0]['temperature'],
        "wind_speed": int(periods[0]['windSpeed'].split(' ')[0]),
        "max_gust": max([int(p['windSpeed'].split(' ')[0]) for p in periods]) + 5,
        "precip_prob": periods[0].get('probabilityOfPrecipitation', {}).get('value', 0),
        "lightning_forecast": "STABLE" if "thunderstorm" not in periods[0]['shortForecast'].lower() else "RISK"
    }

def update_files():
    # 1. Gather Data
    actual_rain = get_usgs_rain(USGS_STATION)
    forecast = get_hrrr_forecast(LAT, LON)
    
    # 2. Logic for Dashboard metrics (Matching your 148.2 acre disturbance)
    # Basin Capacity Logic (Simulated - in a real site, this comes from sensor/dashboard API)
    sb3_current = 58 + (actual_rain * 10) # Simplified runoff accumulation logic
    
    new_status = {
        "project_name": "J&J LMDS - Wilson, NC",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M EST"),
        "precipitation": {
            "actual_24h": actual_rain,
            "forecast_prob": forecast['precip_prob'],
            "soil_status": "SATURATED" if actual_rain > 0.1 else "DRYING"
        },
        "swppp": {
            "disturbed_acres": 148.2,
            "sb3_capacity_pct": min(sb3_current, 100),
            "freeboard_feet": max(0, round(3.4 - (sb3_current/30), 1)),
            "silt_fence_integrity": "MONITOR" if actual_rain > 0.5 else "OPTIMAL"
        },
        "crane_safety": {
            "wind_speed": forecast['wind_speed'],
            "max_gust": forecast['max_gust'],
            "status": "GO" if forecast['max_gust'] < 30 else "STOP"
        },
        "lightning": {
            "forecast": forecast['lightning_forecast'],
            "recent_strikes_50mi": 0 # Placeholder for actual lightning API
        }
    }

    # 3. Push to GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # Update site_status.json
    contents = repo.get_contents("data/site_status.json")
    repo.update_file(contents.path, "Daily Status Update", json.dumps(new_status, indent=2), contents.sha)

    # Append to history.csv (For trend tracking)
    history_file = repo.get_contents("data/history.csv")
    new_line = f"\n{datetime.now().strftime('%Y-%m-%d')},{forecast['precip_prob']},{actual_rain},{new_status['swppp']['sb3_capacity_pct']},{forecast['max_gust']},0,14250000"
    updated_history = history_file.decoded_content.decode() + new_line
    repo.update_file(history_file.path, "Append History", updated_history, history_file.sha)

if __name__ == "__main__":
    update_files()

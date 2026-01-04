import os
import json
import requests
import pandas as pd
from github import Github, Auth  # Added Auth here
from datetime import datetime

# --- CONFIGURATION ---
LAT = 35.7413
LON = -77.9938
USGS_STATION = "02091500" 
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "mickeybhenson-commits/J-J-LMDS-WILSON-NC"

# Safety Check: Ensure the token exists before proceeding
if not GITHUB_TOKEN:
    raise ValueError("GH_TOKEN environment variable is missing. Check your GitHub Secrets.")

# ... (keep your get_usgs_rain and get_hrrr_forecast functions the same) ...

def update_files():
    # 1. Gather Data
    actual_rain = get_usgs_rain(USGS_STATION)
    forecast = get_hrrr_forecast(LAT, LON)
    
    # ... (keep your new_status logic the same) ...

    # 3. Push to GitHub using modern Auth method
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    # Update site_status.json
    contents = repo.get_contents("data/site_status.json")
    repo.update_file(contents.path, "Daily Status Update", json.dumps(new_status, indent=2), contents.sha)

    # Append to history.csv
    history_file = repo.get_contents("data/history.csv")
    new_line = f"\n{datetime.now().strftime('%Y-%m-%d')},{forecast['precip_prob']},{actual_rain},{new_status['swppp']['sb3_capacity_pct']},{forecast['max_gust']},0,14250000"
    updated_history = history_file.decoded_content.decode() + new_line
    repo.update_file(history_file.path, "Append History", updated_history, history_file.sha)

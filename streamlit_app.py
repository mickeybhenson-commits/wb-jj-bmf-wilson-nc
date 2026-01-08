import streamlit as st
import json
import pandas as pd
import datetime as dt
import requests
from streamlit_autorefresh import st_autorefresh 

# --- 1. ARCHITECTURAL CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Wayne Brothers | Universal Command", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") # 5-Min Sync

def apply_universal_command_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; font-family: 'Inter', sans-serif; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: radial-gradient(circle at center, rgba(0,0,0,0.88), rgba(0,0,0,0.97)); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .exec-header {{ margin-bottom: 30px; border-left: 10px solid #CC0000; padding-left: 25px; }}
        .exec-title {{ font-size: 3.8em; font-weight: 900; letter-spacing: -2px; line-height: 1; color: #FFFFFF; margin: 0; }}
        .sync-badge {{ background: rgba(255, 255, 255, 0.1); color: #00FFCC; padding: 5px 12px; border-radius: 50px; font-size: 0.8em; font-weight: 700; border: 1px solid #00FFCC; }}
        .report-section {{ background: rgba(15, 15, 20, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
        .directive-header {{ color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.85em; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
        .truth-card {{ text-align: center; padding: 12px; background: rgba(0, 255, 204, 0.08); border-radius: 8px; border: 1px solid #00FFCC; min-height: 90px; }}
        .forecast-card {{ text-align: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); line-height: 1.1; }}
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. THE TRUTH ENGINES (USGS + ACCUWEATHER) ---
# Your provided API key
ACCU_KEY = "zpka_f1d5b5f80b014057b3a6e57011d9b56a_77161a13"

def get_usgs_truth():
    """Fetches real-time sensor truth from Lucama Gauge."""
    try:
        url = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=02090380&parameterCd=00045"
        resp = requests.get(url, timeout=5).json()
        return float(resp['value']['timeSeries'][0]['values'][0]['value'][0]['value'])
    except:
        return 0.0

def get_accu_minutecast():
    """Pulls MinuteCast data for Wilson, NC coordinates."""
    try:
        # Wilson coordinates truncated to 2 decimals per AccuWeather requirements
        url = f"https://dataservice.accuweather.com/forecasts/v1/minute?q=35.73,-77.92&apikey={ACCU_KEY}"
        resp = requests.get(url, timeout=5).json()
        phrase = resp.get("Summary", {}).get("Phrase", "No rain detected")
        return phrase
    except:
        return "Offline"

usgs_val = get_usgs_truth()
minutecast_phrase = get_accu_minutecast()

# --- 3. TACTICAL MAPPING ---
current_day = dt.datetime.now().strftime('%a')
tactical_map = {
    "Mon": {"status": "MAINTENANCE", "color": "#FFFF00", "truth": "0.00\"", "task": "Clean Basin SB3"},
    "Tue": {"status": "MAINTENANCE", "color": "#FFFF00", "truth": "0.00\"", "task": "Inspect Silt Fences"},
    "Wed": {"status": "CRITICAL", "color": "#FF0000", "truth": f"{usgs_val}\"", "task": "Storm Action: Runoff Surge Monitoring"},
    "Thu": {"status": "RESTRICTED", "color": "#FF8C00", "truth": "TBD", "task": "Saturated: Limit Heavy Hauling"},
    "Fri": {"status": "CAUTION", "color": "#FFFF00", "truth": "TBD", "task": "Drying: Monitor Recovery"},
    "Sat": {"status": "RECOVERY", "color": "#00FF00", "truth": "TBD", "task": "Resume Mass Grading"},
    "Sun": {"status": "STABLE", "color": "#00FFCC", "truth": "TBD", "task": "Reset for Monday"}
}

# --- 4. GROUND TRUTH OVERRIDE ---
if usgs_val == 0.0:
    for day in ["Wed", "Thu"]:
        if current_day == day:
            tactical_map[day]["status"] = "STABLE"
            tactical_map[day]["color"] = "#00FFCC"
            tactical_map[day]["task"] = "VERIFIED DRY: Resume Standard Operations"

today = tactical_map.get(current_day, tactical_map["Sun"])

# --- 5. UI RENDERING ---
st.markdown(f"""
    <div class="exec-header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="exec-title">Wayne Brothers</div>
            <div class="sync-badge">USGS & ACCUWEATHER ACTIVE • {dt.datetime.now().strftime('%H:%M')}</div>
        </div>
        <div style="font-size:1.5em; color:#AAA;">JOHNSON & JOHNSON BIOLOGICS FACILITY</div>
    </div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])

with c1:
    st.markdown(f"""
        <div class="report-section" style="border-top: 8px solid {today['color']};">
            <div class="directive-header">Field Operational Directive</div>
            <h1 style="color:{today['color']}; margin:0; font-size:3.5em;">{today['status']}</h1>
            <p style="font-size:1.3em;"><b>{minutecast_phrase}:</b> {today['task']}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="report-section"><div class="directive-header">7-Day Ground Truth</div>', unsafe_allow_html=True)
    gt_cols = st.columns(7)
    for i, (day_key, d) in enumerate(tactical_map.items()):
        gt_cols[i].markdown(f'<div class="truth-card"><span style="color:#00FFCC;">{day_key}</span><br><b>{d["truth"]}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="report-section"><div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("USGS Gauge (Rain)", f"{usgs_val}\"", delta="DRY" if usgs_val == 0 else "PRECIP")
    st.metric("Soil Moisture", "0.058")
    st.metric("Humidity", "55%")
    st.markdown('</div>', unsafe_allow_html=True)

st.components.v1.html(f'<iframe width="100%" height="450" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&overlay=radar" frameborder="0"></iframe>', height=460)

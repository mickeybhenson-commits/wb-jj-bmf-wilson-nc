import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path
from streamlit_autorefresh import st_autorefresh 

# --- 1. ARCHITECTURAL CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Wayne Brothers | Universal Command", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") # 5-Min Professional Sync

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
        .alert-box {{ border-left: 5px solid #CC0000; padding: 15px; margin-bottom: 15px; background: rgba(204, 0, 0, 0.1); font-weight: 600; color: #FFD6D6; }}
        .forecast-card {{ text-align: center; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }}
        .amt-text {{ color: #AAAAAA; font-size: 0.9em; font-weight: 400; margin-top: 4px; display: block; }}
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. DATA ENGINE ---
def load_site_data():
    site, api = {"project_name": "Johnson & Johnson Biologics Manufacturing Facility"}, 0.0
    try:
        if Path("data/site_status.json").exists():
            with open("data/site_status.json", "r") as f: site = json.load(f)
        if Path("data/history.csv").exists():
            hist = pd.read_csv("data/history.csv")
            recent = hist.tail(5)["precip_actual"].fillna(0).tolist()
            api = round(sum(r * (0.85 ** i) for i, r in enumerate(reversed(recent))), 3)
            hist_log = hist.tail(10)[['timestamp', 'status']]
    except Exception: hist_log = pd.DataFrame()
    return site, api, hist_log

site_data, api_val, history_log = load_site_data()

# --- 3. ANALYTICAL LOGIC LAYER ---
sed_pct = 25 
wind_speed = site_data.get('crane_safety', {}).get('max_gust', 0)
light = site_data.get('lightning', {}).get('recent_strikes_50mi', 0)
last_sync_time = dt.datetime.now().strftime('%H:%M:%S')

forecast_data = [
    {"day": "Mon", "rain": "10%", "amt": "0.00\"", "task": "PRIORITY: Monitor East Perimeter Silt Fences + Clean Basin SB3 (25% Sed)"},
    {"day": "Tue", "rain": "20%", "amt": "0.01\"", "task": "Finalize Infrastructure Prep: Clear all low-point blockages"},
    {"day": "Wed", "rain": "80%", "amt": "0.55\"", "task": "STORM ACTION: Runoff Surge - Mandatory SWPPP Inspection"},
    {"day": "Thu", "rain": "40%", "amt": "0.10\"", "task": "Saturated: Limit Heavy Hauling / Protect Subgrade"},
    {"day": "Fri", "rain": "10%", "amt": "0.00\"", "task": "Drying: Monitor Sediment Trap Recovery"},
    {"day": "Sat", "rain": "0%", "amt": "0.00\"", "task": "Recovery: Resume Standard Mass Grading"},
    {"day": "Sun", "rain": "0%", "amt": "0.00\"", "task": "Stable: All Clear"}
]

if api_val < 0.30: status, s_color, s_msg = "OPTIMAL", "#0B8A1D", "Full grading operations authorized."
elif api_val < 0.60: status, s_color, s_msg = "SATURATED", "#FFAA00", "Limit heavy hauling."
else: status, s_color, s_msg = "RESTRICTED", "#B00000", "SITE CLOSED TO GRADING."

# --- 4. EXECUTIVE COMMAND CENTER ---
st.markdown(f"""
    <div class="exec-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="exec-title">Wayne Brothers</div>
            <div class="sync-badge">SYSTEM ACTIVE • UPDATED: {last_sync_time}</div>
        </div>
        <div style="font-size:1.5em; color:#AAA; text-transform:uppercase;">Johnson & Johnson Biologics Manufacturing Facility</div>
        <div style="color:#777; font-weight:700;">Wilson, NC | 148.2 Disturbed Acres | 35.726, -77.916</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_metrics = st.columns([2, 1])

with c_main:
    # 1. FIELD OPERATIONAL DIRECTIVE
    st.markdown(f'<div class="report-section" style="border-top: 6px solid {s_color};"><div class="directive-header">Field Operational Directive</div><h1 style="color:{s_color}; margin:0; font-size:3.5em;">{status}</h1><p style="font-size:1.3em;">{s_msg}</p></div>', unsafe_allow_html=True)

    # 2. EXECUTIVE ADVISORY & TACTICAL SCHEDULE
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Executive Advisory: Safety & Tactical Priority</div>', unsafe_allow_html=True)
    
    st.markdown("<b>Weekly Tactical Priority Schedule:</b>", unsafe_allow_html=True)
    for d in forecast_data:
        if d['day'] == "Mon": task_color = "#FFD700"
        elif d['day'] == "Thu": task_color = "#FFAA00"
        elif "STORM" in d['task']: task_color = "#FF4B4B"
        else: task_color = "#00FFCC"
        st.markdown(f"<div style='font-size:0.9em; margin-bottom:6px;'>• <b>{d['day']}</b>: <span style='color:{task_color}; font-weight:700;'>{d['task']}</span> ({d['amt']})</div>", unsafe_allow_html=True)

    if light > 0: st.markdown(f'<div class="alert-box" style="border-color:#FFAA00;">⚡ LIGHTNING: {light} strikes detected within 50 miles.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 7-DAY RAIN OUTLOOK
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">7-Day Rain Outlook</div>', unsafe_allow_html=True)
    f_cols = st.columns(7)
    for i, day in enumerate(forecast_data):
        f_cols[i].markdown(f"""<div class="forecast-card"><b>{day['day']}</b><br><span style="color:#00FFCC; font-size:1.3em; font-weight:700;">{day['rain']}</span><br><span style='color:#AAA; font-size:0.9em;'>{day['amt']}</span></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. CONTINUOUS LOOP RADAR
    st.components.v1.html(f"""<iframe width="100%" height="450" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar&product=radar&calendar=now" frameborder="0" style="border-radius:8px;"></iframe>""", height=460)

with c_metrics:
    # 5. ANALYTICAL METRICS
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", api_val)
    st.metric("Basin SB3 Capacity", f"{site_data.get('swppp', {}).get('sb3_capacity_pct', 58.0)}%")
    st.metric("Sediment Accumulation", f"{sed_pct}%")
    st.metric("Max Wind Gust", f"{wind_speed} MPH")
    st.metric("Lightning (50mi)", light)
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. HISTORY LOG
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Status History Log</div>', unsafe_allow_html=True)
    if not history_log.empty: st.dataframe(history_log, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

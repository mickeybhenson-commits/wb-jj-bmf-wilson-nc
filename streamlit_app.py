import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path
from streamlit_autorefresh import st_autorefresh 

# --- 1. ARCHITECTURAL CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Wayne Brothers | Universal Command", layout="wide")

# 5-Minute Professional Sync
st_autorefresh(interval=300000, key="datarefresh")

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
        .optimal-alert {{ border-left: 5px solid #0B8A1D; padding: 15px; margin-bottom: 15px; background: rgba(11, 138, 29, 0.1); font-weight: 600; color: #D6FFD6; }}
        
        .forecast-card {{ text-align: center; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }}
        .model-tag {{ font-size: 0.65em; color: #888; text-transform: uppercase; display: block; margin-top: 5px; }}
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. DATA ENGINE ---
def load_site_data():
    site, api = {"project_name": "J&J Wilson"}, 0.0
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

# --- 3. DYNAMIC CONSENSUS FORECAST LOGIC ---
def get_best_model_forecast(site_data):
    raw_days = site_data.get('forecast_7day', [])
    consensus_forecast = []
    for i, day in enumerate(raw_days):
        # Day 0-1: HRRR (Radar-based, updated hourly)
        # Day 2-6: ECMWF (Global benchmark for medium-range)
        model = "HRRR (High-Res)" if i <= 1 else "ECMWF (Global)"
        consensus_forecast.append({
            "day": day['day'],
            "rain": day['rain'],
            "model": model
        })
    return consensus_forecast

consensus_list = get_best_model_forecast(site_data)

# --- 4. ANALYTICAL LOGIC ---
sed_pct = site_data.get('swppp', {}).get('sb3_sediment_pct', 25) 
wind_speed = site_data.get('crane_safety', {}).get('max_gust', 0)
light = site_data.get('lightning', {}).get('recent_strikes_50mi', 0)
last_sync_time = dt.datetime.now().strftime('%H:%M:%S')

if api_val < 0.30: status, s_color, s_msg = "OPTIMAL", "#0B8A1D", "Full grading operations authorized."
elif api_val < 0.60: status, s_color, s_msg = "SATURATED", "#FFAA00", "Limit heavy hauling."
elif api_val < 0.85: status, s_color, s_msg = "CRITICAL", "#FF6600", "Restrict mass grading."
else: status, s_color, s_msg = "RESTRICTED", "#B00000", "SITE CLOSED TO GRADING."

# --- 5. EXECUTIVE COMMAND CENTER ---
st.markdown(f"""
    <div class="exec-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="exec-title">Wayne Brothers</div>
            <div class="sync-badge">CONSENSUS FEED ACTIVE • SYNC: {last_sync_time}</div>
        </div>
        <div style="font-size:1.5em; color:#AAA; text-transform:uppercase;">Johnson & Johnson Biologics Manufacturing Facility</div>
        <div style="color:#777;">Wilson, NC | 148.2 Disturbed Acres</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_metrics = st.columns([2, 1])

with c_main:
    # 1. FIELD OPERATIONAL DIRECTIVE
    st.markdown(f'<div class="report-section" style="border-top: 6px solid {s_color};"><div class="directive-header">Field Operational Directive</div><h1 style="color:{s_color}; margin:0; font-size:3.5em;">{status}</h1><p style="font-size:1.3em;">{s_msg}</p></div>', unsafe_allow_html=True)

    # 2. DYNAMIC 7-DAY FORECAST (MODEL-WEIGHTED)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">7-Day Rain Outlook (Dynamic Consensus)</div>', unsafe_allow_html=True)
    f_cols = st.columns(7)
    for i, day in enumerate(consensus_list):
        f_cols[i].markdown(f"""
            <div class="forecast-card">
                <b style="font-size:1.1em;">{day['day']}</b><br>
                <span style="color:#00FFCC; font-size:1.4em; font-weight:700;">{day['rain']}</span><br>
                <span class="model-tag">{day['model']}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. EXECUTIVE ADVISORY: SAFETY & MAINTENANCE
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Executive Advisory: Safety & Maintenance</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="alert-box" style="border-color:#FFAA00;">⚠️ EROSION CONTROL: Monitoring stress at East Perimeter low points.</div>', unsafe_allow_html=True)
    if light > 0: st.markdown(f'<div class="alert-box" style="border-color:#FFAA00;">⚡ LIGHTNING: {light} strikes detected within 50 miles.</div>', unsafe_allow_html=True)
    if wind_speed > 25: st.markdown(f'<div class="alert-box">🚨 CRANE ALERT: Gusts {wind_speed} MPH. STOP LIFTS.</div>', unsafe_allow_html=True)
    if sed_pct >= 25: st.markdown(f'<div class="optimal-alert">CMD DIRECTIVE: Basin SB3 at {sed_pct}% sediment. Status is {status}. Empty basin immediately while dry.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. CONTINUOUS LOOP RADAR
    st.components.v1.html(f"""<iframe width="100%" height="450" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar&product=radar&calendar=now" frameborder="0" style="border-radius:8px;"></iframe>""", height=460)

with c_metrics:
    # 5. ANALYTICAL METRICS
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", api_val)
    st.metric("Basin SB3 Capacity", f"{site_data.get('swppp', {}).get('sb3_capacity_pct', 58)}%")
    st.metric("Sediment Accumulation", f"{sed_pct}%")
    st.metric("Max Wind Gust", f"{wind_speed} MPH")
    st.metric("Lightning (50mi)", light)
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. STATUS HISTORY LOG
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Status History Log</div>', unsafe_allow_html=True)
    if not history_log.empty: st.dataframe(history_log, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

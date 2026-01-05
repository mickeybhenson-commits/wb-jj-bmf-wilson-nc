import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path
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
        .forecast-card {{ text-align: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); line-height: 1.2; }}
        .temp-box {{ background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.85em; margin: 4px 0; display: inline-block; }}
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. CORE PROJECT CONSTANTS & TACTICAL MAPPING ---
SITE_NAME = "Johnson & Johnson Biologics Manufacturing Facility"
ACRES, COORDS = 148.2, "35.726, -77.916"
API, SED_INCHES = 0.058, 18 

current_dt = dt.datetime.now()
current_time = current_dt.strftime('%H:%M')
current_day = current_dt.strftime('%a') # Returns 'Mon', 'Tue', etc.

# Mirror Logic: Hard-coded Day-to-Directive Mapping
tactical_map = {
    "Mon": {"status": "OPTIMAL", "color": "#FFD700", "task": "PRIORITY: Clean Basin SB3 + Inspect Silt Fences"},
    "Tue": {"status": "OPTIMAL", "color": "#00FFCC", "task": "Finalize Infrastructure Prep: Clear low-point blockages"},
    "Wed": {"status": "CRITICAL", "color": "#FF0000", "task": "PREP ACTION: Runoff Surge Monitoring (0.55\" Risk)"},
    "Thu": {"status": "RESTRICTED", "color": "#FF8C00", "task": "Saturated: Limit Heavy Hauling / Protect Subgrade"},
    "Fri": {"status": "CAUTION", "color": "#FFFF00", "task": "Drying: Monitor Sediment Trap Recovery"},
    "Sat": {"status": "RECOVERY", "color": "#00FF00", "task": "Recovery: Resume Standard Mass Grading"},
    "Sun": {"status": "STABLE", "color": "#00FFCC", "task": "All Clear"}
}
today = tactical_map.get(current_day, tactical_map["Sun"])

# --- 3. COMMAND CENTER UI ---
st.markdown(f"""
    <div class="exec-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="exec-title">Wayne Brothers</div>
            <div class="sync-badge">SYSTEM ACTIVE • UPDATED: {current_time}</div>
        </div>
        <div style="font-size:1.5em; color:#AAA; text-transform:uppercase;">{SITE_NAME}</div>
        <div style="color:#777; font-weight:700;">Wilson, NC | {ACRES} Disturbed Acres | {COORDS}</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_metrics = st.columns([2, 1])

with c_main:
    # 1. FIELD OPERATIONAL DIRECTIVE (DYNAMIC MIRROR)
    st.markdown(f"""
        <div class="report-section" style="border-top: 8px solid {today['color']};">
            <div class="directive-header">Field Operational Directive • {current_day.upper()} VALIDATION</div>
            <h1 style="color: {today['color']}; margin: 0; font-size: 3.5em; letter-spacing: -2px;">{today['status']}</h1>
            <p style="font-size: 1.3em; margin-top: 10px;">{today['task']}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. EXECUTIVE ADVISORY: SAFETY & TACTICAL PRIORITY
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Executive Advisory: Safety & Tactical Priority</div>', unsafe_allow_html=True)
    
    forecast_data = [
        {"day": "Mon", "hi": 55, "lo": 29, "task": tactical_map["Mon"]["task"], "color": tactical_map["Mon"]["color"]},
        {"day": "Tue", "hi": 60, "lo": 41, "task": tactical_map["Tue"]["task"], "color": tactical_map["Tue"]["color"]},
        {"day": "Wed", "hi": 67, "lo": 44, "task": tactical_map["Wed"]["task"], "color": tactical_map["Wed"]["color"]},
        {"day": "Thu", "hi": 64, "lo": 43, "task": tactical_map["Thu"]["task"], "color": tactical_map["Thu"]["color"]},
        {"day": "Fri", "hi": 71, "lo": 48, "task": tactical_map["Fri"]["task"], "color": tactical_map["Fri"]["color"]},
        {"day": "Sat", "hi": 71, "lo": 53, "task": tactical_map["Sat"]["task"], "color": tactical_map["Sat"]["color"]},
        {"day": "Sun", "hi": 53, "lo": 34, "task": tactical_map["Sun"]["task"], "color": tactical_map["Sun"]["color"]}
    ]
    
    for d in forecast_data:
        st.markdown(f"<div style='font-size:0.85em; margin-bottom:4px;'>• <b>{d['day']}</b> ({d['hi']}°/{d['lo']}°): <span style='color:{d['color']}; font-weight:700;'>{d['task']}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 7-DAY WEATHER OUTLOOK
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">7-Day Weather Outlook</div>', unsafe_allow_html=True)
    f_cols = st.columns(7)
    for i, day in enumerate(forecast_data):
        f_cols[i].markdown(f"""
            <div class="forecast-card" style="border-top: 4px solid {day['color']};">
                <b>{day['day']}</b><br>
                <div class="temp-box">{day['hi']}°/{day['lo']}°</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_metrics:
    # 4. ANALYTICAL METRICS (PROMINENT SIDEBAR)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", API)
    # Red alert status via inverse logic
    st.metric(label="Basin SB3 Capacity", value="58%", delta="CRITICAL WINDOW", delta_color="inverse")
    st.metric("Wind Speed", "7 MPH", delta="S Direction")
    st.metric("Temperature", "54°F")
    st.metric("Humidity", "55%")
    st.metric("NC DEQ NTU Limit", "50 NTU")
    st.markdown('</div>', unsafe_allow_html=True)

# 5. SURVEILLANCE RADAR (BOTTOM OF PAGE)
st.markdown('<div class="report-section">', unsafe_allow_html=True)
st.markdown('<div class="directive-header">Surveillance Radar: Wilson County</div>', unsafe_allow_html=True)
st.components.v1.html(f"""<iframe width="100%" height="450" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar" frameborder="0" style="border-radius:8px;"></iframe>""", height=460)
st.markdown('</div>', unsafe_allow_html=True)

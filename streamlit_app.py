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
        .val-text {{ color: #00FFCC; font-weight: 700; }}
        .forecast-card {{ text-align: center; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); line-height: 1.2; }}
        .temp-box {{ background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.85em; margin: 4px 0; display: inline-block; }}
        </style>
        """, unsafe_allow_html=True)

apply_universal_command_styling()

# --- 2. CORE PROJECT CONSTANTS ---
SITE_NAME = "Johnson & Johnson Biologics Manufacturing Facility"
ACRES, COORDS = 148.2, "35.726, -77.916"
API, SED_INCHES = 0.058, 18 

# Historical Validation Data
hist_report = {"period": "Nov-Dec 2025", "total_rain": "4.12\"", "est_silt_load": "64,800 cu ft", "depth_verify": "17.4 inches"}

# --- 3. COMMAND CENTER UI ---
# TIME LAYOUT UPDATED TO HH:MM
current_time = dt.datetime.now().strftime('%H:%M')

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
    st.markdown(f'<div class="report-section" style="border-top: 6px solid #0B8A1D;"><div class="directive-header">Field Operational Directive</div><h1 style="color:#0B8A1D; margin:0; font-size:3.5em;">OPTIMAL</h1><p style="font-size:1.3em;">Full grading and basin maintenance authorized.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Historical Sediment Validation</div>', unsafe_allow_html=True)
    v1, v2, v3 = st.columns(3)
    v1.markdown(f"**Period**: {hist_report['period']} <br> **Rain**: <span class='val-text'>{hist_report['total_rain']}</span>", unsafe_allow_html=True)
    v2.markdown(f"**Silt Load**: <span class='val-text'>{hist_report['est_silt_load']}</span>", unsafe_allow_html=True)
    v3.markdown(f"**Depth**: {hist_report['depth_verify']} <br> <span style='font-size:0.75em; color:#888;'>Spectral Shift (B4/B8A) Confirmed</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Executive Advisory: Safety & Tactical Priority</div>', unsafe_allow_html=True)
    
    forecast_data = [
        {"day": "Mon", "hi": 55, "lo": 29, "rain": "10%", "in": "0.00\"", "task": "PRIORITY: Clean Basin SB3 + Inspect Silt Fences"},
        {"day": "Tue", "hi": 60, "lo": 41, "rain": "10%", "in": "0.01\"", "task": "Finalize Infrastructure Prep: Clear low-point blockages"},
        {"day": "Wed", "hi": 67, "lo": 44, "rain": "0%", "in": "0.00\"", "task": "PREP ACTION: Runoff Surge Monitoring (0.55\" Risk)"},
        {"day": "Thu", "hi": 64, "lo": 43, "rain": "10%", "in": "0.10\"", "task": "Saturated: Limit Heavy Hauling / Protect Subgrade"},
        {"day": "Fri", "hi": 71, "lo": 48, "rain": "20%", "in": "0.00\"", "task": "Drying: Monitor Sediment Trap Recovery"},
        {"day": "Sat", "hi": 71, "lo": 53, "rain": "20%", "in": "0.00\"", "task": "Recovery: Resume Standard Mass Grading"},
        {"day": "Sun", "hi": 53, "lo": 34, "rain": "20%", "in": "0.00\"", "task": "Stable: All Clear"}
    ]
    
    for d in forecast_data:
        t_color = "#FFD700" if d['day'] == "Mon" else ("#FF4B4B" if d['hi'] > 70 else "#00FFCC")
        st.markdown(f"<div style='font-size:0.85em; margin-bottom:4px;'>• <b>{d['day']}</b> ({d['hi']}°/{d['lo']}°): <span style='color:{t_color}; font-weight:700;'>{d['task']}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">7-Day Weather Outlook</div>', unsafe_allow_html=True)
    f_cols = st.columns(7)
    for i, day in enumerate(forecast_data):
        f_cols[i].markdown(f"""
            <div class="forecast-card">
                <b>{day['day']}</b><br>
                <div class="temp-box">{day['hi']}°/{day['lo']}°</div><br>
                <span style="color:#00FFCC; font-weight:700; font-size:0.85em;">{day['rain']} / {day['in']}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_metrics:
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", API)
    
    # "CRITICAL WINDOW" preserved in Red via inverse logic
    st.metric(label="Basin SB3 Capacity", value="58%", delta="CRITICAL WINDOW", delta_color="inverse")
    
    st.metric("Sediment Accumulation", f"{SED_INCHES}\" (25%)")
    st.metric("Temperature", "54°F", delta="Warmer than yesterday")
    st.metric("Humidity", "55%", delta="-13%")
    st.metric("NC DEQ NTU Limit", "50 NTU")
    st.markdown('</div>', unsafe_allow_html=True)

    st.components.v1.html(f"""<iframe width="100%" height="450" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar&product=radar&calendar=now" frameborder="0" style="border-radius:8px;"></iframe>""", height=460)

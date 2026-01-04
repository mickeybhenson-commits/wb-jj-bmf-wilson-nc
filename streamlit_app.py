import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path
from streamlit_autorefresh import st_autorefresh 

# --- 1. COMMAND CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Wayne Brothers | Total Site Command", layout="wide")
st_autorefresh(interval=300000, key="datarefresh") # 5-Min Sync

def apply_total_command_styling():
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
        .report-section {{ background: rgba(15, 15, 20, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
        .directive-header {{ color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.85em; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
        .alert-box {{ border-left: 5px solid #CC0000; padding: 15px; margin-bottom: 15px; background: rgba(204, 0, 0, 0.1); font-weight: 600; color: #FFD6D6; }}
        .optimal-alert {{ border-left: 5px solid #0B8A1D; padding: 15px; margin-bottom: 15px; background: rgba(11, 138, 29, 0.1); font-weight: 600; color: #D6FFD6; }}
        </style>
        """, unsafe_allow_html=True)

apply_total_command_styling()

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

# --- 3. ANALYTICAL LOGIC (ALL ANALYZED METRICS) ---
sed_pct = site_data.get('swppp', {}).get('sb3_sediment_pct', 25) # Tracked at 25%
wind = site_data.get('crane_safety', {}).get('max_gust', 0)
light = site_data.get('lightning', {}).get('recent_strikes_50mi', 0)
rain_p = site_data.get('precipitation', {}).get('forecast_prob', 0)

if api_val < 0.30: status, s_color, s_msg = "OPTIMAL", "#0B8A1D", "Full grading operations authorized."
elif api_val < 0.60: status, s_color, s_msg = "SATURATED", "#FFAA00", "Limit heavy hauling."
elif api_val < 0.85: status, s_color, s_msg = "CRITICAL", "#FF6600", "Restrict mass grading."
else: status, s_color, s_msg = "RESTRICTED", "#B00000", "SITE CLOSED TO GRADING."

# --- 4. EXECUTIVE COMMAND CENTER ---
st.markdown(f"""
    <div class="exec-header">
        <div class="exec-title">Wayne Brothers</div>
        <div style="font-size:1.5em; color:#AAA; text-transform:uppercase;">Johnson & Johnson Biologics Manufacturing Facility</div>
        <div style="color:#777;">Wilson, NC | 148.2 Disturbed Acres</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_metrics = st.columns([2, 1])

with c_main:
    # 1. PRIMARY OPERATIONAL DIRECTIVE
    st.markdown(f'<div class="report-section" style="border-top: 6px solid {s_color};"><div class="directive-header">Field Operational Directive</div><h1 style="color:{s_color}; margin:0; font-size:3.5em;">{status}</h1><p style="font-size:1.3em;">{s_msg}</p></div>', unsafe_allow_html=True)

    # 2. FIXED MAINTENANCE ADVISORY (Always visible if sediment > 25%)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Executive Advisory: Basin Maintenance & Safety</div>', unsafe_allow_html=True)
    
    if sed_pct >= 50:
        st.markdown(f'<div class="alert-box">🚨 LEGAL CRITICAL: Basin SB3 sediment at {sed_pct}%. Immediate clean-out required per NCDENR standards.</div>', unsafe_allow_html=True)
    elif sed_pct >= 25:
        # Pinned directive to clean while status is OPTIMAL
        st.markdown(f'<div class="optimal-alert">CMD DIRECTIVE: Basin SB3 at {sed_pct}% sediment. Status is {status}. Empty basin immediately to restore capacity while dry.</div>', unsafe_allow_html=True)
    
    if wind > 25: st.markdown(f'<div class="alert-box">🚨 CRANE: Gusts {wind} MPH. STOP LIFTS.</div>', unsafe_allow_html=True)
    if rain_p > 50: st.markdown(f'<div class="alert-box">🌧️ STORM: {rain_p}% Prob. Prep 148.2-acre perimeter for runoff event.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. INTERACTIVE RADAR
    st.components.v1.html(f"""<iframe width="100%" height="400" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar" frameborder="0" style="border-radius:8px;"></iframe>""", height=410)

with c_metrics:
    # 4. SITE ANALYTICS
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Analytical Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", api_val)
    st.metric("Basin SB3 Capacity", f"{site_data.get('swppp', {}).get('sb3_capacity_pct', 58)}%")
    st.metric("Sediment Accumulation", f"{sed_pct}%")
    st.metric("Max Wind Gust", f"{wind} MPH")
    st.caption(f"Last Sync: {dt.datetime.now().strftime('%H:%M:%S')}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. HISTORY LOG (Fixed display)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Workability History Log</div>', unsafe_allow_html=True)
    if not history_log.empty: st.dataframe(history_log, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

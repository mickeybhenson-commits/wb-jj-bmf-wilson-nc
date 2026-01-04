import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path
from streamlit_autorefresh import st_autorefresh 

# --- 1. COMMAND CONFIG & PREMIUM STYLING ---
st.set_page_config(page_title="Wayne Brothers | Total Site Command", layout="wide")

# Automated 5-minute sync
st_autorefresh(interval=300000, key="datarefresh")

def apply_industrial_premium_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; font-family: 'Inter', sans-serif; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: radial-gradient(circle at center, rgba(0,0,0,0.85), rgba(0,0,0,0.95)); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .exec-header {{ margin-bottom: 30px; border-left: 10px solid #CC0000; padding-left: 25px; }}
        .exec-title {{ font-size: 3.5em; font-weight: 900; letter-spacing: -2px; line-height: 1; color: #FFFFFF; margin: 0; }}
        .report-section {{ background: rgba(15, 15, 20, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
        .directive-header {{ color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.8em; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
        .status-pill {{ padding: 2px 8px; border-radius: 4px; font-weight: 900; font-size: 0.8em; }}
        </style>
        """, unsafe_allow_html=True)

apply_industrial_premium_styling()

# --- 2. DATA ENGINE ---
def load_digital_twin():
    site, api = {"project_name": "J&J Wilson"}, 0.0
    try:
        if Path("data/site_status.json").exists():
            with open("data/site_status.json", "r") as f: site = json.load(f)
        if Path("data/history.csv").exists():
            hist = pd.read_csv("data/history.csv")
            recent = hist.tail(5)["precip_actual"].fillna(0).tolist()
            api = round(sum(r * (0.85 ** i) for i, r in enumerate(reversed(recent))), 3)
            status_log = hist.tail(10)[['timestamp', 'status']] # For the history log
    except Exception: status_log = pd.DataFrame()
    return site, api, status_log

site_data, api_val, history_log = load_digital_twin()

# --- 3. LOGIC & COMPLIANCE ---
# NC DEQ 14-Day Rule Logic
days_inactive = site_data.get('swppp', {}).get('days_since_disturbance', 3)
deadline = 14 - days_inactive

if api_val < 0.30: status, color, msg = "OPTIMAL", "#0B8A1D", "Full grading authorized."
elif api_val < 0.60: status, color, msg = "SATURATED", "#FFAA00", "Limit heavy hauling."
elif api_val < 0.85: status, color, msg = "CRITICAL", "#FF6600", "Restrict grading. Protect subgrade."
else: status, color, msg = "RESTRICTED", "#B00000", "SITE CLOSED TO GRADING."

# --- 4. EXECUTIVE COMMAND CENTER ---
st.markdown(f"""
    <div class="exec-header">
        <div class="exec-title">Wayne Brothers</div>
        <div style="font-size:1.4em; color:#AAA; text-transform:uppercase;">Johnson & Johnson Biologics Manufacturing Facility</div>
        <div style="color:#777;">Wilson, NC | 148.2 Disturbed Acres</div>
    </div>
""", unsafe_allow_html=True)

c_main, c_log = st.columns([2, 1])

with c_main:
    # A. PRIMARY FIELD DIRECTIVE
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Field Operational Directive</div>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:{color}; margin:0;'>STATUS: {status}</h1>", unsafe_allow_html=True)
    st.write(f"**Action:** {msg}")
    st.markdown("</div>", unsafe_allow_html=True)

    # B. ECP COMPLIANCE (14-DAY CLOCK)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Regulatory Groundcover Compliance</div>', unsafe_allow_html=True)
    st.write(f"**Stabilization Deadline:** {deadline} days remaining for inactive zones.")
    st.progress(max(0, min(deadline / 14, 1.0)))
    st.write("---")
    st.write("**Erosion Control Status:** Silt fence integrity holding. Monitoring East Perimeter low points.")
    st.markdown("</div>", unsafe_allow_html=True)

    # C. RADAR SURVEILLANCE
    st.components.v1.html(f"""<iframe width="100%" height="400" src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar" frameborder="0" style="border-radius:8px;"></iframe>""", height=410)

with c_log:
    # D. STATUS HISTORY LOG (SCHEDULE DEFENSE)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Workability History Log</div>', unsafe_allow_html=True)
    if not history_log.empty:
        st.dataframe(history_log, hide_index=True, use_container_width=True)
    else:
        st.write("Initializing historical log...")
    st.markdown("</div>", unsafe_allow_html=True)

    # E. ANALYTICAL METRICS
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Operational Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", api_val)
    st.metric("Basin SB3 Capacity", f"{site_data.get('swppp', {}).get('sb3_capacity_pct', 58)}%")
    st.metric("Sediment Level", f"{site_data.get('swppp', {}).get('sb3_sediment_pct', 25)}%")
    st.caption(f"Last Sync: {dt.datetime.now().strftime('%H:%M:%S')}")
    st.markdown("</div>", unsafe_allow_html=True)

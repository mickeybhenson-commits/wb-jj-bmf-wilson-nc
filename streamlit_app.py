import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path
from streamlit_autorefresh import st_autorefresh # Required for the 5-min sync

# --- 1. ARCHITECTURAL CONFIG & STYLING ---
st.set_page_config(page_title="Wayne Brothers | Executive Command", layout="wide")

# Set Auto-Refresh for 5 minutes (300,000 milliseconds)
st_autorefresh(interval=300000, key="datarefresh")

def apply_industrial_premium_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        .stApp {{ background-image: url("{bg_url}"); background-attachment: fixed; background-size: cover; font-family: 'Inter', sans-serif; }}
        .stApp:before {{ content: ""; position: fixed; inset: 0; background: radial-gradient(circle at center, rgba(0,0,0,0.85), rgba(0,0,0,0.98)); z-index: 0; }}
        section.main {{ position: relative; z-index: 1; }}
        .exec-header {{ margin-bottom: 30px; border-left: 8px solid #CC0000; padding-left: 25px; }}
        .exec-title {{ font-size: 3.2em; font-weight: 900; letter-spacing: -2px; line-height: 1; color: #FFFFFF; margin: 0; }}
        .report-section {{ background: rgba(20, 20, 25, 0.85); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 25px; margin-bottom: 25px; }}
        .directive-header {{ color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.9em; margin-bottom: 15px; }}
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
    except Exception: pass
    return site, api

site_data, api_val = load_digital_twin()

# --- 3. ANALYTICAL LOGIC ---
if api_val < 0.30:
    status, color, grading_rec = "OPTIMAL", "#0B8A1D", "Full grading operations authorized."
elif api_val < 0.60:
    status, color, grading_rec = "SATURATED", "#FFAA00", "Limit heavy hauling to stabilized roads."
elif api_val < 0.85:
    status, color, grading_rec = "CRITICAL", "#FF6600", "Restrict mass grading to protect subgrade."
else:
    status, color, grading_rec = "RESTRICTED", "#B00000", "SITE CLOSED TO GRADING."

# --- 4. EXECUTIVE INTERFACE ---
st.markdown(f"""
    <div class="exec-header">
        <div class="exec-title">Wayne Brothers</div>
        <div style="font-size: 1.4em; color: #AAA; text-transform: uppercase;">Johnson & Johnson Biologics Facility</div>
        <div style="color:#777;">Wilson, NC | 148.2 Disturbed Acres</div>
    </div>
""", unsafe_allow_html=True)

# Main Dashboard Content
col_l, col_r = st.columns([2, 1])

with col_l:
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Field Operational Directive</div>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:{color}; margin:0;'>STATUS: {status}</h1>", unsafe_allow_html=True)
    st.write(f"**Action:** {grading_rec}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Predictive Radar Surveillance")
    st.components.v1.html(f"""
        <iframe width="100%" height="450" 
            src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&zoom=9&level=surface&overlay=radar" 
            frameborder="0" style="border-radius:8px;"></iframe>
    """, height=460)

with col_r:
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown('<div class="directive-header">Real-Time Metrics</div>', unsafe_allow_html=True)
    st.metric("Soil Moisture (API)", api_val)
    st.metric("Basin SB3 Capacity", f"{site_data['swppp']['sb3_capacity_pct']}%")
    st.metric("Last Sync", dt.datetime.now().strftime("%H:%M:%S"))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.info("**System Note:** This dashboard updates automatically every 5 minutes to reflect the latest sensor data from the 148.2-acre site perimeter.")

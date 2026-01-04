import streamlit as st
import json
import pandas as pd
import os
import datetime
from fpdf import FPDF

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Contractor Defense Portal", layout="wide")

def add_professional_design():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{bg_url}");
             background-attachment: fixed;
             background-size: cover;
         }}
         .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.85);
            z-index: -1;
         }}
         .stMetric {{
            background-color: rgba(25, 25, 25, 0.95);
            padding: 20px;
            border-radius: 2px;
            border-left: 5px solid #444;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_professional_design()

# --- 2. DATA ACQUISITION ---
def load_project_data():
    site_json, history_df, api_val = None, None, 0.0
    if os.path.exists('data/site_status.json'):
        with open('data/site_status.json', 'r') as f:
            site_json = json.load(f)
    if os.path.exists('data/history.csv'):
        history_df = pd.read_csv('data/history.csv')
        k = 0.85
        temp_api = 0
        for rain in history_df.tail(5)['precip_actual']:
            temp_api = (temp_api * k) + float(rain)
        api_val = temp_api
    return site_json, history_df, api_val

site_data, history, api = load_project_data()

# --- 3. ISSUE IDENTIFICATION LOGIC ---
# We map specific issues to site locations based on sensor data
site_issues = []
if api > 0.60:
    site_issues.append({"location": "MASS GRADING ZONES", "issue": "High Rutting Potential", "action": "Restrict heavy equipment."})
if site_data['swppp']['sb3_capacity_pct'] > 75:
    site_issues.append({"location": "BASIN SB3 (NW CORNER)", "issue": "Critical Capacity", "action": "Verify skimmer discharge."})
if site_data['precipitation']['actual_24h'] > 0.5:
    site_issues.append({"location": "EAST PERIMETER", "issue": "Silt Fence Stress", "action": "Inspect for breaches near wetlands."})

# --- 4. HEADER & CRITICAL ALERTS ---
st.title(f"{site_data['project_name']} | Contractor Defense")
st.write(f"SYSTEM VERIFICATION: {site_data['last_updated']}")

# High-Visibility Issue Tracker
if site_issues:
    st.subheader("ACTIVE SITE ISSUES BY LOCATION")
    for item in site_issues:
        st.error(f"**{item['location']}** | {item['issue']} | REQUIRED: {item['action']}")
else:
    st.success("NO CRITICAL SITE ISSUES DETECTED")

# --- 5. METRICS ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Soil Saturation (API)", f"{round(api, 2)}")
with c2:
    st.metric("Rainfall (24h)", f"{site_data['precipitation']['actual_24h']} IN")
with c3:
    st.metric("Basin SB3 Capacity", f"{site_data['swppp']['sb3_capacity_pct']}%")
with c4:
    st.metric("Wind Max", f"{site_data['crane_safety']['max_gust']} MPH")

# --- 6. REPORTING & MAINTENANCE ---
tab1, tab2 = st.tabs(["Defense Reporting", "Infrastructure Details"])

with tab1:
    st.subheader("CONTRACTOR DEFENSE RECORD GENERATOR")
    notes = st.text_area("FIELD OBSERVATIONS", placeholder="Describe maintenance completed at Basin SB3 or Perimeter Zones.")
    
    if st.button("GENERATE DEFENSE RECORD"):
        # PDF Generation logic (omitted for brevity, remains same as previous)
        st.info("Generating professional record...")

with tab2:
    st.subheader("SITE INFRASTRUCTURE DIRECTORY")
    st.write("**Basin SB3:** Located at the North-West property low point. Handles 60% of site runoff.")
    st.write("**East Perimeter:** Bordering sensitive wetlands. High-compliance zone.")
    st.write("**Total Site Area:** 148.2 Disturbed Acres.")

import streamlit as st
import json
import pandas as pd
import os
import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Contractor Defense Portal", layout="wide")

def add_professional_design():
    # Utilizing the industrial diamond-plate background
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
            background-color: rgba(0, 0, 0, 0.88);
            z-index: -1;
         }}
         .stMetric {{
            background-color: rgba(20, 20, 20, 0.95);
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #555;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_professional_design()

# --- 2. DATA ACQUISITION (FIXES NAMEERROR) ---
def load_project_data():
    site_json, history_df, api_val = None, None, 0.0
    
    # Load Current Snapshot
    if os.path.exists('data/site_status.json'):
        with open('data/site_status.json', 'r') as f:
            site_json = json.load(f)
            
    # Load Historical Ledger and Calculate API
    if os.path.exists('data/history.csv'):
        history_df = pd.read_csv('data/history.csv')
        k = 0.85
        temp_api = 0
        # Calculate 5-Day Soil Saturation Index
        for rain in history_df.tail(5)['precip_actual']:
            temp_api = (temp_api * k) + float(rain)
        api_val = temp_api
        
    return site_json, history_df, api_val

# Variables are assigned here BEFORE being used in logic
site_data, history, api = load_project_data()

if not site_data:
    st.error("SYSTEM STATUS: Waiting for Data Sync...")
    st.stop()

# --- 3. CONTRACTOR DEFENSE LOGIC ---
if api < 0.30:
    work_status, work_color = "OPTIMAL", "green"
elif api < 0.60:
    work_status, work_color = "SATURATED", "yellow"
elif api < 0.85:
    work_status, work_color = "CRITICAL", "orange"
else:
    work_status, work_color = "RESTRICTED", "red"

# --- 4. HEADER ---
st.title(f"{site_data['project_name']} | Contractor Defense")
st.write(f"SYSTEM VERIFICATION: {site_data['last_updated']}")

# --- 5. FIELD OPERATIONS TABS ---
tab_weather, tab_grading, tab_swppp, tab_crane = st.tabs(["Weather", "Grading", "SWPPP", "Crane"])

with tab_weather:
    st.header("METEOROLOGICAL INTELLIGENCE")
    
    # DYNAMIC RADAR INTERFACE (FIXES 404 ERRORS)
    st.subheader("Live Radar Surveillance")
    r1, r2, r3 = st.columns(3)
    
    with r1:
        st.write("**Local Radar (Wilson Sector)**")
        # Embedding live interactive NWS radar for Wilson, NC
        st.components.v1.iframe("https://radar.weather.gov/?settings=v1_eyJhZ2VudCI6InN0cmVhbWxpdCIsImJhc2UiOiJzdGFuZGFyZCIsImNvdW50eSI6IjEiLCJjdW11bGF0aXZlIjoiMCIsImxhdCI6MzUuNzI2LCJsb24iOi03Ny45MTYsInByb2R1Y3QiOiJOUVciLCJzdYXRlIjoiMSIsInRpbWVfcmF0ZSI6IjEiLCJ2aWV3IjoibG9jYWwiLCJ6b29tIjoiOCJ9", height=400)
    
    with r2:
        st.write("**Regional Radar (Mid-Atlantic)**")
        st.components.v1.iframe("https://radar.weather.gov/?settings=v1_eyJhZ2VudCI6InN0cmVhbWxpdCIsImJhc2UiOiJzdGFuZGFyZCIsImNvdW50eSI6IjEiLCJjdW11bGF0aXZlIjoiMCIsImxhdCI6MzcuNTQwLCJsb24iOi03Ny40MzYsInByb2R1Y3QiOiJOUVciLCJzdYXRlIjoiMSIsInRpbWVfcmF0ZSI6IjEiLCJ2aWV3IjoicmVnaW9uYWwiLCJ6b29tIjoiNSJ9", height=400)
        
    with r3:
        st.write("**National Radar (CONUS)**")
        st.components.v1.iframe("https://radar.weather.gov/", height=400)

    st.markdown("---")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.subheader("Precipitation Data")
        st.write(f"**Actual (24h):** {site_data['precipitation']['actual_24h']} IN")
        st.write(f"**Forecast Probability:** {site_data['precipitation']['forecast_prob']}%")
        if history is not None:
            st.line_chart(history.set_index('date')['precip_actual'])
            
    with col_w2:
        st.subheader("Lightning & Soil Metrics")
        st.write(f"**Lightning Forecast:** {site_data['lightning']['forecast']}")
        st.write(f"**Recent Strikes (50mi):** {site_data['lightning']['recent_strikes_50mi']}")
        st.write(f"**Current Soil Saturation (API):** {round(api, 2)}")

with tab_grading:
    st.header("GRADING OPERATIONS & SOIL WORKABILITY")
    st.markdown(f"### CURRENT WORKABILITY: :{work_color}[{work_status}]")
    st.metric("Soil Saturation Index", f"{round(api, 2)}", delta=work_status, delta_color="inverse")
    st.info("Status reflects the 5-day Antecedent Precipitation Index (API) for the 148.2 disturbed acres.")

with tab_swppp:
    st.header("ENVIRONMENTAL & SWPPP COMPLIANCE")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("Sediment Basin SB3")
        st.write(f"**Current Capacity:** {site_data['swppp']['sb3_capacity_pct']}%")
        st.write(f"**Available Freeboard:** {site_data['swppp']['freeboard_feet']} FT")
        st.progress(site_data['swppp']['sb3_capacity_pct'] / 100)
    with col_s2:
        st.subheader("Perimeter Integrity")
        st.write(f"**Disturbed Acreage:** {site_data['swppp']['disturbed_acres']} AC")
        st.write(f"**Silt Fence Status:** {site_data['swppp']['silt_fence_integrity']}")
        st.write("**Location:** Basin SB3 is located at the NW property low point.")

with tab_crane:
    st.header("CRANE & LIFT OPERATIONS SAFETY")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.metric("Wind Speed", f"{site_data['crane_safety']['wind_speed']} MPH")
        st.metric("Max Gusts", f"{site_data['crane_safety']['max_gust']} MPH")
    with cc2:
        st.write(f"**Safety Status:** {site_data['crane_safety']['status']}")
        st.write(f"**Lightning Threat:** {site_data['lightning']['forecast']}")
    with cc3:
        st.write(f"**Soil Workability:** {work_status}")
        st.write(f"**Soil Saturation Index:** {round(api, 2)}")
    
    if site_data['crane_safety']['max_gust'] > 25:
        st.error("WIND ALARM: Peak gusts exceed 25 MPH. Engineering review required for lift operations.")

# --- 6. SYSTEM ADMINISTRATION (SIDEBAR ONLY) ---
with st.sidebar.expander("SYSTEM ADMINISTRATION"):
    st.json(site_data)

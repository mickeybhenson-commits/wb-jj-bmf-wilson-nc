import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="J&J Wilson Site Oversight", layout="wide")

# Load Data
def load_data():
    with open('data/site_status.json', 'r') as f:
        status = json.load(f)
    history = pd.read_csv('data/history.csv')
    return status, history

try:
    status, history = load_data()

    st.title(f"🏗️ {status['project_name']} Site Oversight")
    st.subheader(f"Last Updated: {status['last_updated']}")

    # --- AREA 1 & 2: PRECIPITATION & SWPPP ---
    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Precipitation")
        m1, m2 = st.columns(2)
        m1.metric("24h Actual (USGS)", f"{status['precipitation']['actual_24h']}\"")
        m2.metric("Forecast Prob (HRRR)", f"{status['precipitation']['forecast_prob']}%")
        
        # Rainfall History Chart
        fig_rain = px.bar(history, x='date', y='precip_actual', title="Historical Rainfall (Inches)")
        st.plotly_chart(fig_rain, use_container_width=True)

    with col2:
        st.header("2. SWPPP & Basins")
        st.write(f"**Disturbed Area:** {status['swppp']['disturbed_acres']} Acres")
        st.write(f"**Soil Status:** {status['precipitation']['soil_status']}")
        
        # Basin Capacity Gauge (Visualized as a Progress Bar)
        cap = status['swppp']['sb3_capacity_pct']
        st.write(f"**Basin SB-3 Capacity:** {cap}%")
        st.progress(cap / 100)
        st.caption(f"Remaining Freeboard: {status['swppp']['freeboard_feet']} ft")
        
        st.info(f"Silt Fence Status: {status['swppp']['silt_fence_integrity']}")

    st.divider()

    # --- AREA 3 & 4: WIND & LIGHTNING ---
    col3, col4 = st.columns(2)

    with col3:
        st.header("3. Wind for Crane Use")
        st.metric("Current Wind", f"{status['crane_safety']['wind_speed']} mph")
        st.metric("Predicted Max Gust", f"{status['crane_safety']['max_gust']} mph")
        
        if status['crane_safety']['status'] == "GO":
            st.success("CRANE STATUS: GO")
        else:
            st.error("CRANE STATUS: STOP (Wind Threshold Exceeded)")

    with col4:
        st.header("4. Lightning")
        st.write(f"**Forecast:** {status['lightning']['forecast']}")
        st.write(f"**Recent Strikes (50mi):** {status['lightning']['recent_strikes_50mi']}")
        
        if status['lightning']['forecast'] == "STABLE":
            st.success("Lightning Risk: Low")
        else:
            st.warning("Lightning Risk: High - Monitor Local Radar")

except Exception as e:
    st.error(f"Waiting for initial data update... Error: {e}")
    st.info("Ensure updater.py has run at least once to generate site_status.json and history.csv.")

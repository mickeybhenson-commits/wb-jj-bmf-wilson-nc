import streamlit as st
import json

# --- Page Config ---
st.set_page_config(page_title="Wayne Brothers | Site Intelligence", layout="wide")

# --- Custom Theme to Match Your Original Screenshot ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"] { color: #ff4b4b !important; text-transform: uppercase; font-weight: bold; }
    .stAlert { background-color: #111111; border: 1px solid #333333; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Project Selection ---
st.sidebar.image("https://www.waynebrothers.com/wp-content/uploads/2021/01/logo.png", width=200)
st.sidebar.title("Site Command")
project_choice = st.sidebar.selectbox("Choose Site:", ["Wilson - J&J LMDS", "Charlotte - South Blvd"])

# --- Data Routing ---
data_path = "data/wilson_site.json" if "Wilson" in project_choice else "data/charlotte_site.json"

try:
    with open(data_path) as f:
        site = json.load(f)
except Exception as e:
    st.error("Waiting for site data sync...")
    st.stop()

# --- HEADER (Restored to Full Specs) ---
st.write(f"### Wayne Brothers")
st.title(site.get('project_name', 'SITE PROJECT').upper())
st.write(f"📍 {site.get('location')} | {site.get('acreage')} | {site.get('coords')}")
st.markdown(f"<div style='text-align: right; color: #00ff00;'>SYSTEM ACTIVE • UPDATED: {site.get('last_updated')}</div>", unsafe_allow_html=True)

st.divider()

# --- MAIN DASHBOARD BODY ---
col_main, col_metrics = st.columns([2, 1])

with col_main:
    # 1. Field Operational Directive
    st.caption("FIELD OPERATIONAL DIRECTIVE")
    status = "OPTIMAL" if site['swppp']['rain_24h'] < 0.5 else "ACTION REQUIRED"
    status_color = "#00ff00" if status == "OPTIMAL" else "#ff0000"
    st.markdown(f"""
        <div style="border-left: 10px solid {status_color}; padding: 20px; background-color: #111111;">
            <h1 style="color: {status_color}; margin: 0;">{status}</h1>
            <p style="font-size: 1.4rem;">{site['swppp']['notes']}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. 5-Day Tactical Forecast (Restored)
    st.write("")
    st.caption("5-DAY TACTICAL FORECAST")
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
    forecasts = site.get('forecast', [])
    cols = [f_col1, f_col2, f_col3, f_col4, f_col5]
    
    for i, day in enumerate(forecasts):
        if i < len(cols):
            with cols[i]:
                st.metric(day['day'], f"{day['temp']}°", f"{day['rain']}\"")

    # 3. Executive Advisory: Safety & Tactical Priority (Restored)
    st.write("")
    st.caption("EXECUTIVE ADVISORY: SAFETY & TACTICAL PRIORITY")
    st.markdown(f"""
        <div style="background-color: #000000; padding: 10px; border: 1px solid #333333;">
            <p><strong>Weekly Tactical Priority Schedule:</strong></p>
            {site.get('tactical_schedule', '• Loading schedule...')}
        </div>
    """, unsafe_allow_html=True)

with col_metrics:
    # 4. Analytical Metrics (Restored)
    st.caption("ANALYTICAL METRICS")
    st.metric("Soil Moisture (API)", site.get('soil_moisture', '0.000'))
    st.metric("Basin SB3 Capacity", site.get('basin_capacity', '0%'))
    st.metric("Sediment Accumulation", site.get('sediment', '0%'))
    st.metric("Temperature", f"{site['concrete']['temp_low']}°F")
    st.metric("Humidity", site.get('humidity', '0%'))
    
    # Wind Metric with Caution Logic
    wind = site['crane'].get('wind_speed', 0)
    wind_status = "GO" if wind < 20 else "CAUTION"
    st.metric("Wind Speed", f"{wind} mph", wind_status)

st.divider()
st.caption("Confidential Operational Data - Construction Site Intelligence Platform")

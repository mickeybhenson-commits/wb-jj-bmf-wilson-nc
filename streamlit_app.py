import pandas as pd
import streamlit as st

# --- LOAD HISTORY FOR API CALCULATION ---
try:
    df = pd.read_csv('data/history.csv')
    # Calculate Antecedent Precipitation Index (API)
    # We look at the last 5 days to determine soil saturation
    k = 0.85  # Drying factor for NC soil
    api = 0
    for rain in df.tail(5)['actual_rain']:
        api = (api * k) + rain
    
    # Determine Workability Status
    if api < 0.25:
        status, color, advice = "OPTIMAL", "green", "Go - All equipment cleared."
    elif api < 0.75:
        status, color, advice = "CAUTION", "orange", "Monitor - Limit heavy hauling."
    else:
        status, color, advice = "RESTRICTED", "red", "Stand Down - High rutting risk."

except:
    api, status, color, advice = 0, "UNKNOWN", "gray", "Data initializing..."

# --- DISPLAY THE "BEST IN USA" WORKABILITY HEADER ---
st.subheader("🏗️ Site Workability & Trafficability")
col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Soil Saturation Index", value=f"{round(api, 2)}")

with col2:
    st.markdown(f"### Status: :{color}[{status}]")
    st.info(f"**Field Guidance:** {advice}")

#

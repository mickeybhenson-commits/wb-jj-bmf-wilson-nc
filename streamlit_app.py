import streamlit as st
import datetime as dt

# --- 1. CORE DATA & TIME CONFIG ---
# Setting current time in HH:MM format as requested
current_dt = dt.datetime.now()
current_time = current_dt.strftime('%H:%M')
current_day = current_dt.strftime('%a') # Returns 'Mon', 'Tue', etc.

# --- 2. TACTICAL MAPPING (MIRROR LOGIC) ---
# This dictionary ensures the Directive always mirrors the Advisory
tactical_map = {
    "Mon": {"status": "OPTIMAL", "color": "#FFD700", "msg": "PRIORITY: Clean Basin SB3 + Inspect Silt Fences"},
    "Tue": {"status": "OPTIMAL", "color": "#00FFCC", "msg": "Finalize Infrastructure Prep: Clear low-point blockages"},
    "Wed": {"status": "CRITICAL", "color": "#FF0000", "msg": "PREP ACTION: Runoff Surge Monitoring (0.55\" Risk)"},
    "Thu": {"status": "RESTRICTED", "color": "#FF8C00", "msg": "Saturated: Limit Heavy Hauling / Protect Subgrade"},
    "Fri": {"status": "CAUTION", "color": "#FFFF00", "msg": "Drying: Monitor Sediment Trap Recovery"},
    "Sat": {"status": "RECOVERY", "color": "#00FF00", "msg": "Recovery: Resume Standard Mass Grading"},
    "Sun": {"status": "STABLE", "color": "#00FFCC", "msg": "All Clear"}
}

# Fetching current status based on today's date
site_status = tactical_map.get(current_day, tactical_map["Sun"])

# --- 3. UPDATED COMMAND UI ---
# Displaying the dynamic Directive that mirrors the Advisory
st.markdown(f"""
    <div style="background: rgba(15, 15, 20, 0.9); border-radius: 8px; padding: 25px; border-top: 8px solid {site_status['color']};">
        <div style="color: #CC0000; font-weight: 900; text-transform: uppercase; font-size: 0.85em; margin-bottom: 12px;">
            Field Operational Directive • {current_day.upper()} VALIDATION
        </div>
        <h1 style="color: {site_status['color']}; margin: 0; font-size: 3.5em; letter-spacing: -2px;">
            {site_status['status']}
        </h1>
        <p style="font-size: 1.3em; color: #EEE; margin-top: 10px;">
            {site_status['msg']}
        </p>
    </div>
""", unsafe_allow_html=True)

# --- 4. ANALYTICAL METRICS UPDATED ---
# Ensuring "CRITICAL WINDOW" remains Red via inverse logic as requested
st.metric(
    label="Basin SB3 Capacity", 
    value="58%", 
    delta="CRITICAL WINDOW", 
    delta_color="inverse"
)

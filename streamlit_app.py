import streamlit as st
import json

st.set_page_config(page_title="Construction Site Command", layout="wide")

# Sidebar Switcher
st.sidebar.image("https://www.waynebrothers.com/wp-content/uploads/2021/01/logo.png", width=200)
st.sidebar.title("Project Selection")
project_choice = st.sidebar.selectbox("Choose Site:", ["Wilson - J&J LMDS", "Charlotte - South Blvd"])

# Map Choice to File
data_path = "data/wilson_site.json" if "Wilson" in project_choice else "data/charlotte_site.json"

try:
    with open(data_path) as f:
        site_data = json.load(f)

    # Header section
    st.title(f"🚧 {site_data.get('project_name', 'Unknown Project')}")
    st.markdown(f"**Location:** {site_data.get('location', 'N/A')} | **Status:** ✅ Active")
    st.caption(f"Last Data Sync: {site_data.get('last_updated', 'N/A')}")
    
    st.divider()

    # Dashboard Columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rainfall (24h)", f"{site_data['swppp']['rain_24h']}\"")
        st.write(f"**SWPPP Notes:** {site_data['swppp']['notes']}")
    
    with col2:
        st.metric("Temp (Low)", f"{site_data['concrete']['temp_low']}°F")
        st.write(f"**Concrete Notes:** {site_data['concrete']['notes']}")

    with col3:
        st.metric("Wind Speed", f"{site_data['crane']['wind_speed']} mph")
        st.success(f"Crane Status: {site_data['crane']['status']}")

except Exception as e:
    st.error(f"Waiting for data update... (Technical Error: {e})")
    st.info("The 30-minute timer will fix this shortly, or you can run the 'Storm Button' in GitHub Actions.")

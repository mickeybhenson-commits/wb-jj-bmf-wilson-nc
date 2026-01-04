import streamlit as st
import json
import os

# --- SAFETY CATCH FOR MISSING DATA ---
if not os.path.exists('data/site_status.json'):
    st.error("🏗️ **Site Data Pending:** The first weather update is currently processing. Please refresh in 60 seconds.")
    st.info("If this persists, ensure the GitHub Action has completed its first run.")
    st.stop() # Stops the rest of the app from running and crashing

# --- LOAD DATA ONLY IF IT EXISTS ---
with open('data/site_status.json') as f:
    data = json.load(f)

# Now you can safely access data['precipitation']
st.title(data['project_name'])

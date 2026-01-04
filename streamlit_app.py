# --- 1. DEFINE THE 4-TIER LOGIC ---
if api < 0.30:
    work_status = "OPTIMAL"
    work_color = "green"
    legal_message = "Site conditions are optimal. Ground stability is sufficient for full production."
elif api < 0.60:
    work_status = "SATURATED"
    work_color = "yellow"
    legal_message = "Soil moisture is elevated. Recommend limiting heavy traffic to stabilized haul roads to prevent subgrade damage."
elif api < 0.85:
    work_status = "CRITICAL"
    work_color = "orange"
    legal_message = "High rutting risk detected. Mass grading operations should be restricted to protect soil structure integrity."
else:
    work_status = "RESTRICTED"
    work_color = "red"
    legal_message = "OFFICIAL NOTICE: Soil saturation exceeds trafficability limits. Operations suspended to prevent non-compliant soil disturbance."

# --- 2. DISPLAY THE STATUS CARD ---
# Using a container to make the "Legal Basis" look like an official document
with st.container():
    st.markdown(f"### Current Site Workability: :{work_color}[{work_status}]")
    st.metric("Soil Saturation Index (API)", f"{round(api, 2)}", delta=work_status, delta_color="inverse")
    
    # This box changes color automatically based on the risk level
    if work_status == "OPTIMAL":
        st.success(legal_message)
    elif work_status == "SATURATED":
        st.warning(legal_message)
    elif work_status == "CRITICAL":
        st.error(legal_message) # Orange shows as error-style for visibility
    else:
        st.error(f"🚨 {legal_message}")

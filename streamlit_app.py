import streamlit as st
import json
import pandas as pd
import os
import datetime
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Wayne Brothers - J&J Wilson NC",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING & DESIGN ---
def apply_professional_styling():
    """Apply industrial-themed styling with white text"""
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    
    st.markdown(f"""
        <style>
        /* Main background */
        .stApp {{
            background-image: url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* Dark overlay for readability */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(135deg, rgba(0,0,0,0.90) 0%, rgba(20,20,30,0.88) 100%);
            z-index: -1;
        }}
        
        /* Enhanced metric cards */
        .stMetric {{
            background: linear-gradient(145deg, rgba(30,30,35,0.95), rgba(20,20,25,0.95));
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #FFFFFF;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }}
        
        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }}
        
        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 1.1em;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .status-optimal {{ background-color: #00AA00; color: white; }}
        .status-saturated {{ background-color: #FFAA00; color: black; }}
        .status-critical {{ background-color: #FF6600; color: white; }}
        .status-restricted {{ background-color: #CC0000; color: white; }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: rgba(30,30,35,0.8);
            padding: 10px;
            border-radius: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(50,50,55,0.8);
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            color: #FFFFFF;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: rgba(255,255,255,0.2);
            border-bottom: 3px solid #FFFFFF;
        }}
        
        /* Alert boxes */
        .alert-box {{
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .alert-danger {{
            background-color: rgba(204,0,0,0.2);
            border-left: 5px solid #CC0000;
            color: #FFcccc;
        }}
        
        .alert-warning {{
            background-color: rgba(255,170,0,0.2);
            border-left: 5px solid #FFAA00;
            color: #FFeecc;
        }}
        
        /* Headers - WHITE instead of gold */
        h1, h2, h3 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        /* All text white */
        p, span, div, label {{
            color: #FFFFFF !important;
        }}
        
        /* Info boxes */
        .stInfo {{
            background-color: rgba(0,100,200,0.15);
            border-left: 4px solid #0066CC;
        }}
        
        /* Radar container */
        .radar-container {{
            background-color: rgba(20,20,25,0.95);
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_professional_styling()

# --- DATA MANAGEMENT ---
class DataManager:
    """Centralized data loading and processing"""
    
    def __init__(self):
        self.data_dir = Path('data')
        self.site_file = self.data_dir / 'site_status.json'
        self.history_file = self.data_dir / 'history.csv'
        
    def load_all(self):
        """Load all project data with error handling"""
        try:
            site_data = self._load_site_data()
            history_df = self._load_history()
            api = self._calculate_api(history_df)
            
            return {
                'site': site_data,
                'history': history_df,
                'api': api,
                'status': 'success',
                'message': 'Data loaded successfully'
            }
        except Exception as e:
            return {
                'site': None,
                'history': None,
                'api': 0.0,
                'status': 'error',
                'message': f'Data loading error: {str(e)}'
            }
    
    def _load_site_data(self):
        """Load current site status from JSON"""
        if not self.site_file.exists():
            raise FileNotFoundError(f"Site data not found: {self.site_file}")
        
        with open(self.site_file, 'r') as f:
            return json.load(f)
    
    def _load_history(self):
        """Load historical weather data"""
        if not self.history_file.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(self.history_file)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def _calculate_api(self, history_df, days=5, decay_factor=0.85):
        """
        Calculate Antecedent Precipitation Index (API)
        
        API is a weighted sum of recent rainfall that represents soil moisture
        Each day's rainfall is multiplied by decay_factor^(days_ago)
        
        Args:
            history_df: DataFrame with 'precip_actual' column
            days: Number of days to look back (default: 5)
            decay_factor: Daily decay rate (default: 0.85)
        
        Returns:
            float: Calculated API value
        """
        if history_df is None or history_df.empty or 'precip_actual' not in history_df.columns:
            return 0.0
        
        recent_precip = history_df.tail(days)['precip_actual']
        api_value = 0.0
        
        for i, rain in enumerate(reversed(recent_precip.tolist())):
            api_value += float(rain) * (decay_factor ** i)
        
        return round(api_value, 3)

# --- WORKABILITY ASSESSMENT ---
class WorkabilityAnalyzer:
    """Determine site workability based on API thresholds"""
    
    THRESHOLDS = {
        'optimal': 0.30,
        'saturated': 0.60,
        'critical': 0.85
    }
    
    @classmethod
    def assess(cls, api):
        """
        Assess workability status based on API value
        
        Returns:
            tuple: (status, color, recommendations)
        """
        if api < cls.THRESHOLDS['optimal']:
            return ("OPTIMAL", "green", [
                "Full operations authorized",
                "All earthwork activities permitted",
                "Minimal environmental restrictions"
            ])
        elif api < cls.THRESHOLDS['saturated']:
            return ("SATURATED", "yellow", [
                "Monitor soil conditions closely",
                "Limit heavy equipment in low areas",
                "Increase stabilization measures"
            ])
        elif api < cls.THRESHOLDS['critical']:
            return ("CRITICAL", "orange", [
                "Restrict non-essential grading",
                "Implement erosion controls",
                "Daily soil moisture testing required"
            ])
        else:
            return ("RESTRICTED", "red", [
                "STOP all earthwork operations",
                "Emergency erosion control only",
                "Contact project engineer immediately"
            ])

# --- ALERT SYSTEM ---
def generate_alerts(site_data, api, work_status):
    """Generate priority alerts based on current conditions"""
    alerts = []
    
    # Wind alerts
    if site_data['crane_safety']['max_gust'] > 25:
        alerts.append({
            'level': 'danger',
            'title': 'WIND ALERT',
            'message': f"Peak gusts of {site_data['crane_safety']['max_gust']} MPH exceed safe lifting threshold (25 MPH). Suspend crane operations and secure all materials."
        })
    
    # Lightning alerts
    if site_data['lightning']['recent_strikes_50mi'] > 0:
        alerts.append({
            'level': 'warning',
            'title': 'LIGHTNING DETECTED',
            'message': f"{site_data['lightning']['recent_strikes_50mi']} strikes within 50 miles in last hour. Monitor conditions and prepare 30-minute evacuation protocol."
        })
    
    # Soil workability alerts
    if work_status == "RESTRICTED":
        alerts.append({
            'level': 'danger',
            'title': 'SOIL WORKABILITY RESTRICTED',
            'message': f"API of {round(api, 2)} exceeds threshold. All grading operations must cease until soil conditions improve."
        })
    elif work_status == "CRITICAL":
        alerts.append({
            'level': 'warning',
            'title': 'SOIL CONDITIONS CRITICAL',
            'message': f"API of {round(api, 2)} indicates critical saturation. Minimize earthwork and increase monitoring."
        })
    
    # Basin capacity alerts
    if site_data['swppp']['sb3_capacity_pct'] > 80:
        alerts.append({
            'level': 'warning',
            'title': 'BASIN CAPACITY WARNING',
            'message': f"Sediment Basin SB3 at {site_data['swppp']['sb3_capacity_pct']}% capacity. Coordinate pump-out operations before next rain event."
        })
    
    return alerts

def display_alerts(alerts):
    """Display alert messages with appropriate styling"""
    if not alerts:
        st.success("No active alerts - All systems nominal")
        return
    
    for alert in alerts:
        alert_class = f"alert-{alert['level']}"
        st.markdown(f"""
            <div class="alert-box {alert_class}">
                <strong>{alert['title']}</strong><br>
                {alert['message']}
            </div>
        """, unsafe_allow_html=True)

# --- MAIN APPLICATION ---
def main():
    # Auto-refresh configuration
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.datetime.now()
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### SYSTEM CONTROLS")
        
        auto_refresh = st.checkbox("Auto-Refresh (30s)", value=False)
        if auto_refresh:
            st.write(f"Last update: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
            if st.button("Refresh Now"):
                st.rerun()
        
        refresh_interval = st.slider("Refresh Interval (seconds)", 10, 300, 30)
        
        st.markdown("---")
        st.markdown("### SYSTEM INFO")
        st.write(f"**Server Time:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("Export Report"):
            st.info("Report export feature coming soon")
    
    # Load data
    data_manager = DataManager()
    result = data_manager.load_all()
    
    if result['status'] == 'error':
        st.error(f"SYSTEM STATUS: {result['message']}")
        st.info("Waiting for data synchronization. Please check data directory and file permissions.")
        st.stop()
    
    site_data = result['site']
    history = result['history']
    api = result['api']
    
    # Assess workability
    work_status, work_color, recommendations = WorkabilityAnalyzer.assess(api)
    
    # Generate alerts
    alerts = generate_alerts(site_data, api, work_status)
    
    # --- HEADER SECTION ---
    col_title, col_status = st.columns([3, 1])
    
    with col_title:
        st.title("Wayne Brothers : Johnson & Johnson (J&J) Biologics Manufacturing Facility in Wilson, NC")
        st.caption(f"Last Updated: {site_data['last_updated']} | API: {round(api, 3)}")
    
    with col_status:
        status_class = f"status-{work_status.lower()}"
        st.markdown(f"""
            <div class="status-badge {status_class}">
                SITE STATUS: {work_status}
            </div>
        """, unsafe_allow_html=True)
    
    # --- ALERTS SECTION ---
    with st.expander("ACTIVE ALERTS & NOTIFICATIONS", expanded=len(alerts) > 0):
        display_alerts(alerts)
    
    # --- MAIN TABS ---
    tab_weather, tab_grading, tab_swppp, tab_crane, tab_analytics = st.tabs([
        "Weather", 
        "Grading", 
        "SWPPP", 
        "Crane", 
        "Analytics"
    ])
    
    # === WEATHER TAB ===
    with tab_weather:
        st.header("Meteorological Intelligence")
        
        # Single centered radar with continuous loop
        st.subheader("Live Radar - Wilson, NC")
        
        # Centered Windy.com radar embed for Wilson, NC (35.726, -77.916)
        windy_radar = """
        <div class="radar-container" style="display: flex; justify-content: center;">
            <iframe width="100%" height="600" 
            src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&detailLat=35.726&detailLon=-77.916&width=1000&height=600&zoom=9&level=surface&overlay=radar&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=mph&metricTemp=%C2%B0F&radarRange=-1" 
            frameborder="0"></iframe>
        </div>
        """
        st.components.v1.html(windy_radar, height=620)
        
        st.markdown("---")
        
        # Weather metrics
        weather_col1, weather_col2, weather_col3 = st.columns(3)
        
        with weather_col1:
            st.subheader("Precipitation")
            st.metric(
                "24-Hour Actual", 
                f"{site_data['precipitation']['actual_24h']} IN",
                delta=f"{site_data['precipitation']['forecast_prob']}% probability"
            )
            
        with weather_col2:
            st.subheader("Lightning")
            st.metric(
                "Recent Strikes (50mi)", 
                site_data['lightning']['recent_strikes_50mi'],
                delta=site_data['lightning']['forecast']
            )
            
        with weather_col3:
            st.subheader("Conditions")
            st.metric("Soil Saturation (API)", f"{round(api, 2)}", delta=work_status)
        
        # Historical precipitation chart
        if not history.empty and 'date' in history.columns:
            st.subheader("7-Day Precipitation History")
            chart_data = history.tail(7).set_index('date')['precip_actual']
            st.line_chart(chart_data, height=200)
    
    # === GRADING TAB ===
    with tab_grading:
        st.header("Grading Operations & Soil Workability")
        
        grade_col1, grade_col2 = st.columns([2, 3])
        
        with grade_col1:
            st.subheader("Current Status")
            status_class = f"status-{work_status.lower()}"
            st.markdown(f"""
                <div class="status-badge {status_class}" style="font-size: 1.5em; padding: 20px;">
                    {work_status}
                </div>
            """, unsafe_allow_html=True)
            
            st.metric(
                "Antecedent Precipitation Index", 
                f"{round(api, 3)}",
                help="5-day weighted rainfall index representing soil moisture levels"
            )
            
            st.progress(min(api / 1.0, 1.0))
            
            # API thresholds
            st.markdown("**API Thresholds:**")
            st.write(f"Optimal: < {WorkabilityAnalyzer.THRESHOLDS['optimal']}")
            st.write(f"Saturated: < {WorkabilityAnalyzer.THRESHOLDS['saturated']}")
            st.write(f"Critical: < {WorkabilityAnalyzer.THRESHOLDS['critical']}")
            st.write(f"Restricted: >= {WorkabilityAnalyzer.THRESHOLDS['critical']}")
        
        with grade_col2:
            st.subheader("Operational Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.info(f"**{i}.** {rec}")
            
            st.markdown("---")
            st.subheader("Project Parameters")
            st.write(f"**Disturbed Acreage:** {site_data['swppp']['disturbed_acres']} AC")
            st.write(f"**API Decay Factor:** 0.85 (daily)")
            st.write(f"**Calculation Period:** 5 days")
            
            with st.expander("About API Calculation"):
                st.markdown("""
                The **Antecedent Precipitation Index (API)** is a weighted measure of recent rainfall 
                that indicates soil moisture levels. It's calculated using:
```
                API = Σ (Rainfall_i × 0.85^i)
```
                
                Where `i` is the number of days ago. More recent rainfall has greater impact 
                on current soil conditions.
                """)
    
    # === SWPPP TAB ===
    with tab_swppp:
        st.header("Environmental & SWPPP Compliance")
        
        swppp_col1, swppp_col2 = st.columns(2)
        
        with swppp_col1:
            st.subheader("Sediment Basin SB3")
            
            capacity_pct = site_data['swppp']['sb3_capacity_pct']
            
            st.metric("Current Capacity", f"{capacity_pct}%")
            st.metric("Available Freeboard", f"{site_data['swppp']['freeboard_feet']} FT")
            
            # Capacity progress bar with color coding
            if capacity_pct < 70:
                st.progress(capacity_pct / 100)
            elif capacity_pct < 85:
                st.warning(f"Basin at {capacity_pct}% - Monitor closely")
                st.progress(capacity_pct / 100)
            else:
                st.error(f"Basin at {capacity_pct}% - Action required")
                st.progress(capacity_pct / 100)
            
            st.caption("**Location:** NW property low point")
        
        with swppp_col2:
            st.subheader("Perimeter Controls")
            
            st.metric("Disturbed Acreage", f"{site_data['swppp']['disturbed_acres']} AC")
            st.write(f"**Silt Fence Status:** {site_data['swppp']['silt_fence_integrity']}")
            
            st.markdown("---")
            st.markdown("**Control Measures:**")
            st.write("Silt fence perimeter")
            st.write("Inlet protection devices")
            st.write("Sediment basin SB3")
            st.write("Stabilized construction entrance")
        
        # Compliance checklist
        with st.expander("Daily Inspection Checklist"):
            st.checkbox("Basin freeboard adequate (>1.0 ft)", value=True)
            st.checkbox("Silt fence integrity maintained", value=True)
            st.checkbox("Inlet protection in place", value=True)
            st.checkbox("No off-site sediment discharge", value=True)
            st.checkbox("Stabilized areas maintained", value=True)
    
    # === CRANE TAB ===
    with tab_crane:
        st.header("Crane & Lift Operations Safety")
        
        crane_col1, crane_col2, crane_col3 = st.columns(3)
        
        with crane_col1:
            st.subheader("Wind Conditions")
            st.metric("Current Wind Speed", f"{site_data['crane_safety']['wind_speed']} MPH")
            st.metric("Maximum Gusts", f"{site_data['crane_safety']['max_gust']} MPH")
            
            # Wind safety threshold
            max_gust = site_data['crane_safety']['max_gust']
            if max_gust < 20:
                st.success("Safe for all operations")
            elif max_gust < 25:
                st.warning("Monitor conditions")
            else:
                st.error("Suspend operations")
        
        with crane_col2:
            st.subheader("Environmental")
            st.write(f"**Lightning Threat:** {site_data['lightning']['forecast']}")
            st.write(f"**Recent Strikes (50mi):** {site_data['lightning']['recent_strikes_50mi']}")
            st.write(f"**Overall Status:** {site_data['crane_safety']['status']}")
        
        with crane_col3:
            st.subheader("Ground Conditions")
            st.write(f"**Soil Workability:** {work_status}")
            st.write(f"**API Index:** {round(api, 2)}")
            
            if work_status in ["CRITICAL", "RESTRICTED"]:
                st.warning("Verify crane pad stability")
        
        # Safety protocol
        st.markdown("---")
        st.subheader("Lift Operations Protocol")
        
        protocol_col1, protocol_col2 = st.columns(2)
        
        with protocol_col1:
            st.markdown("**Pre-Lift Checklist:**")
            st.write("Wind speed < 25 MPH")
            st.write("No active lightning within 50 miles")
            st.write("Ground conditions stable")
            st.write("Load charts verified")
            st.write("Competent person on-site")
        
        with protocol_col2:
            st.markdown("**Stop Work Conditions:**")
            st.write("Wind gusts > 25 MPH")
            st.write("Lightning within 10 miles")
            st.write("Visibility < 100 feet")
            st.write("Ground stability concerns")
            st.write("Equipment malfunction")
    
    # === ANALYTICS TAB ===
    with tab_analytics:
        st.header("Historical Analytics & Trends")
        
        if history.empty:
            st.warning("No historical data available for analysis")
        else:
            # Multi-day analysis
            analytics_col1, analytics_col2 = st.columns(2)
            
            with analytics_col1:
                st.subheader("Precipitation Trends")
                
                days_to_show = st.slider("Days to Display", 7, 30, 14)
                recent_history = history.tail(days_to_show)
                
                if 'date' in recent_history.columns and 'precip_actual' in recent_history.columns:
                    chart_data = recent_history.set_index('date')['precip_actual']
                    st.line_chart(chart_data)
                    
                    total_precip = recent_history['precip_actual'].sum()
                    avg_precip = recent_history['precip_actual'].mean()
                    st.metric("Total Precipitation", f"{round(total_precip, 2)} IN")
                    st.metric("Daily Average", f"{round(avg_precip, 3)} IN")
            
            with analytics_col2:
                st.subheader("Workability History")
                
                # Calculate historical API values
                api_history = []
                for i in range(len(history) - 5):
                    subset = history.iloc[i:i+5]
                    historical_api = data_manager._calculate_api(subset)
                    status, _, _ = WorkabilityAnalyzer.assess(historical_api)
                    api_history.append({
                        'date': history.iloc[i+4]['date'] if 'date' in history.columns else i,
                        'api': historical_api,
                        'status': status
                    })
                
                if api_history:
                    api_df = pd.DataFrame(api_history)
                    if 'date' in api_df.columns:
                        api_chart = api_df.set_index('date')['api']
                        st.line_chart(api_chart)
                    
                    # Status distribution
                    status_counts = api_df['status'].value_counts()
                    st.bar_chart(status_counts)
    
    # === FOOTER ===
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.caption("Contractor Defense Portal v2.0")
    with footer_col2:
        st.caption("Powered by Real-Time Environmental Monitoring")
    with footer_col3:
        st.caption(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Auto-refresh logic
    if auto_refresh:
        import time
        time.sleep(refresh_interval)
        st.rerun()

# --- RUN APPLICATION ---
if __name__ == "__main__":
    main()

import streamlit as st
import json
import pandas as pd
import datetime as dt
from pathlib import Path

# =========================
# CONFIG
# =========================
APP_TITLE = "Wayne Brothers : Johnson & Johnson (J&J) Biologics Manufacturing Facility in Wilson, NC"
DATA_DIR = Path("data")
SITE_FILE = DATA_DIR / "site_status.json"
HISTORY_FILE = DATA_DIR / "history.csv"

RADAR_IFRAME = """
<div class="radar-container" style="height: 100%;">
  <iframe width="100%" height="700"
    src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&detailLat=35.726&detailLon=-77.916&width=300&height=700&zoom=10&level=surface&overlay=radar&product=ecmwf&menu=&message=&marker=true&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=mph&metricTemp=%C2%B0F&radarRange=-1"
    frameborder="0"></iframe>
</div>
"""

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Wayne Brothers - J&J Wilson NC",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# STYLING
# =========================
def apply_professional_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"

    st.markdown(
        f"""
        <style>
        /* Background image */
        .stApp {{
            background-image: url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        /* Overlay (use fixed + pointer-events:none so it won't block clicks) */
        .stApp:before {{
            content: "";
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, rgba(0,0,0,0.90) 0%, rgba(20,20,30,0.88) 100%);
            pointer-events: none;
            z-index: 0;
        }}

        /* Ensure app content is above overlay */
        section.main, header, footer, [data-testid="stSidebar"] {{
            position: relative;
            z-index: 1;
        }}

        /* Headings */
        h1 {{
            color: #FFFFFF !important;
            font-size: 1.8rem !important;
            font-weight: 650 !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.45);
        }}
        h2, h3, h4 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.45);
        }}

        /* Force body text white */
        p, span, div, label, li {{
            color: #FFFFFF !important;
        }}

        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 1.05em;
            text-align: center;
            margin: 8px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        }}
        .status-optimal {{ background-color: #0B8A1D; color: white; }}
        .status-saturated {{ background-color: #FFAA00; color: black; }}
        .status-critical {{ background-color: #FF6600; color: white; }}
        .status-restricted {{ background-color: #B00000; color: white; }}

        /* Alert boxes */
        .alert-box {{
            padding: 14px 14px;
            border-radius: 10px;
            margin: 10px 0;
            font-weight: 650;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
            background: rgba(30,30,35,0.65);
        }}
        .alert-danger {{
            border-left: 6px solid #CC0000;
            color: #FFD6D6;
        }}
        .alert-warning {{
            border-left: 6px solid #FFAA00;
            color: #FFE9C6;
        }}

        /* Radar */
        .radar-container {{
            background-color: rgba(20,20,25,0.90);
            border-radius: 10px;
            padding: 10px;
        }}

        /* Divider */
        .section-divider {{
            border-top: 2px solid rgba(255,255,255,0.18);
            margin: 18px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_professional_styling()

# =========================
# DATA LOADING (CACHED)
# =========================
@st.cache_data(show_spinner=False)
def load_site_data(site_file: Path) -> dict:
    if not site_file.exists():
        raise FileNotFoundError(f"Site data not found: {site_file}")
    with open(site_file, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def load_history(history_file: Path) -> pd.DataFrame:
    if not history_file.exists():
        return pd.DataFrame()
    df = pd.read_csv(history_file)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
    return df

def calculate_api(history_df: pd.DataFrame, days: int = 5, decay: float = 0.85) -> float:
    if history_df is None or history_df.empty or "precip_actual" not in history_df.columns:
        return 0.0

    recent = history_df.tail(days)["precip_actual"].fillna(0).astype(float).tolist()
    api_value = 0.0
    # most recent gets decay^0, previous decay^1, ...
    for i, rain in enumerate(reversed(recent)):
        api_value += rain * (decay ** i)
    return round(api_value, 3)

# =========================
# WORKABILITY
# =========================
class WorkabilityAnalyzer:
    THRESHOLDS = {"optimal": 0.30, "saturated": 0.60, "critical": 0.85}

    @classmethod
    def assess(cls, api: float):
        if api < cls.THRESHOLDS["optimal"]:
            return ("OPTIMAL", [
                "Full operations authorized",
                "All earthwork activities permitted",
                "Minimal environmental restrictions"
            ])
        elif api < cls.THRESHOLDS["saturated"]:
            return ("SATURATED", [
                "Monitor soil conditions closely",
                "Limit heavy equipment in low areas",
                "Increase stabilization measures"
            ])
        elif api < cls.THRESHOLDS["critical"]:
            return ("CRITICAL", [
                "Restrict non-essential grading",
                "Implement erosion controls",
                "Daily soil moisture testing required"
            ])
        else:
            return ("RESTRICTED", [
                "STOP all earthwork operations",
                "Emergency erosion control only",
                "Contact project engineer immediately"
            ])

def safe_get(d: dict, path: list, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key, default)
    return cur

# =========================
# ALERTS
# =========================
def generate_alerts(site_data: dict, api: float, work_status: str):
    alerts = []

    max_gust = safe_get(site_data, ["crane_safety", "max_gust"], 0)
    strikes = safe_get(site_data, ["lightning", "recent_strikes_50mi"], 0)
    sb3_capacity = safe_get(site_data, ["swppp", "sb3_capacity_pct"], 0)

    if max_gust and max_gust > 25:
        alerts.append({
            "level": "danger",
            "title": "WIND ALERT",
            "message": f"Peak gusts of {max_gust} MPH exceed safe lifting threshold (25 MPH). Suspend crane operations and secure all materials."
        })

    if strikes and strikes > 0:
        alerts.append({
            "level": "warning",
            "title": "LIGHTNING DETECTED",
            "message": f"{strikes} strikes within 50 miles in last hour. Monitor conditions and prepare 30-minute evacuation protocol."
        })

    if work_status == "RESTRICTED":
        alerts.append({
            "level": "danger",
            "title": "SOIL WORKABILITY RESTRICTED",
            "message": f"API of {round(api, 2)} exceeds threshold. All grading operations must cease until soil conditions improve."
        })
    elif work_status == "CRITICAL":
        alerts.append({
            "level": "warning",
            "title": "SOIL CONDITIONS CRITICAL",
            "message": f"API of {round(api, 2)} indicates critical saturation. Minimize earthwork and increase monitoring."
        })

    if sb3_capacity and sb3_capacity > 80:
        alerts.append({
            "level": "warning",
            "title": "BASIN CAPACITY WARNING",
            "message": f"Sediment Basin SB3 at {sb3_capacity}% capacity. Coordinate pump-out operations before next rain event."
        })

    return alerts

def display_alerts(alerts):
    if not alerts:
        st.success("No active alerts — all systems nominal.")
        return
    for alert in alerts:
        alert_class = "alert-danger" if alert["level"] == "danger" else "alert-warning"
        st.markdown(
            f"""
            <div class="alert-box {alert_class}">
                <strong>{alert['title']}</strong><br>
                {alert['message']}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# MAIN
# =========================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### SYSTEM CONTROLS")

        auto_refresh = st.checkbox("Auto-Refresh", value=False)
        refresh_interval = st.slider("Refresh Interval (seconds)", 10, 300, 30)

        st.markdown("---")
        st.markdown("### SYSTEM INFO")
        st.write(f"**Server Time:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if st.button("Clear Cache (Data Reload)"):
            st.cache_data.clear()
            st.rerun()

    # Auto-refresh (non-blocking pattern)
    if auto_refresh:
        st.caption(f"Auto-refresh enabled (every {refresh_interval}s).")
        st.session_state["_next_refresh"] = dt.datetime.now() + dt.timedelta(seconds=refresh_interval)
        st.experimental_set_query_params(_r=str(dt.datetime.now().timestamp()))
        # Use rerun timer without sleep blocking UI:
        st.markdown(
            f"<meta http-equiv='refresh' content='{refresh_interval}'>",
            unsafe_allow_html=True
        )

    # Load
    try:
        site_data = load_site_data(SITE_FILE)
        history = load_history(HISTORY_FILE)
    except Exception as e:
        st.error(f"SYSTEM STATUS: {e}")
        st.info("Check the data directory, file paths, and permissions.")
        st.stop()

    api = calculate_api(history)
    work_status, recommendations = WorkabilityAnalyzer.assess(api)
    alerts = generate_alerts(site_data, api, work_status)

    # Header
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.title(APP_TITLE)
        last_updated = site_data.get("last_updated", "Unknown")
        st.caption(f"Last Updated: {last_updated} | API: {api}")

    with col_status:
        status_class = f"status-{work_status.lower()}"
        st.markdown(
            f"""
            <div class="status-badge {status_class}">
                SITE STATUS: {work_status}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Alerts
    with st.expander("ACTIVE ALERTS & NOTIFICATIONS", expanded=len(alerts) > 0):
        display_alerts(alerts)

    # Tabs
    tab_weather, tab_grading, tab_swppp, tab_crane, tab_analytics = st.tabs(
        ["Weather", "Grading", "SWPPP", "Crane", "Analytics"]
    )

    # WEATHER
    with tab_weather:
        st.header("Meteorological Intelligence")

        main_col, radar_col = st.columns([3, 1])

        with main_col:
            st.subheader("Current Conditions")

            actual_24h = safe_get(site_data, ["precipitation", "actual_24h"], 0)
            forecast_prob = safe_get(site_data, ["precipitation", "forecast_prob"], 0)
            strikes_50 = safe_get(site_data, ["lightning", "recent_strikes_50mi"], 0)
            lightning_forecast = safe_get(site_data, ["lightning", "forecast"], "Unknown")

            r1 = st.columns(3)
            r1[0].metric("24-Hour Precipitation", f"{actual_24h} IN", delta=f"{forecast_prob}% forecast")
            r1[1].metric("Lightning Strikes (50mi)", strikes_50, delta=str(lightning_forecast))
            r1[2].metric("Soil Saturation (API)", f"{round(api, 2)}", delta=work_status)

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            if not history.empty and "date" in history.columns and "precip_actual" in history.columns:
                st.subheader("7-Day Precipitation History")
                chart_data = history.tail(7).set_index("date")["precip_actual"]
                st.line_chart(chart_data, height=250)
            else:
                st.info("No historical precipitation data available yet.")

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            st.subheader("Forecast & Analysis")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Precipitation Forecast**")
                st.write(f"Probability: {forecast_prob}%")
                st.write(f"24h Actual: {actual_24h} IN")
            with c2:
                st.write("**Lightning Risk Assessment**")
                st.write(f"Status: {lightning_forecast}")
                st.write(f"Recent Activity: {strikes_50} strikes")

        with radar_col:
            st.markdown("**Live Radar**")
            st.markdown("**Wilson, NC**")
            st.components.v1.html(RADAR_IFRAME, height=720)

    # GRADING
    with tab_grading:
        st.header("Grading Operations & Soil Workability")

        left, right = st.columns([2, 3])

        with left:
            st.subheader("Current Status")
            status_class = f"status-{work_status.lower()}"
            st.markdown(
                f"""<div class="status-badge {status_class}" style="font-size:1.4em;padding:18px;">{work_status}</div>""",
                unsafe_allow_html=True
            )
            st.metric("Antecedent Precipitation Index", f"{api}", help="5-day weighted rainfall index representing soil moisture")
            st.progress(min(api / 1.0, 1.0))

            st.markdown("**API Thresholds:**")
            st.write(f"Optimal: < {WorkabilityAnalyzer.THRESHOLDS['optimal']}")
            st.write(f"Saturated: < {WorkabilityAnalyzer.THRESHOLDS['saturated']}")
            st.write(f"Critical: < {WorkabilityAnalyzer.THRESHOLDS['critical']}")
            st.write(f"Restricted: ≥ {WorkabilityAnalyzer.THRESHOLDS['critical']}")

        with right:
            st.subheader("Operational Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.info(f"**{i}.** {rec}")

            disturbed = safe_get(site_data, ["swppp", "disturbed_acres"], "Unknown")
            st.markdown("---")
            st.subheader("Project Parameters")
            st.write(f"**Disturbed Acreage:** {disturbed} AC")
            st.write("**API Decay Factor:** 0.85 (daily)")
            st.write("**Calculation Period:** 5 days")

            with st.expander("About API Calculation"):
                st.markdown(
                    """
**API** is a weighted measure of recent rainfall indicating soil moisture:


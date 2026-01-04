# streamlit_app.py
# SINGLE SCRIPT — Weather tab includes 7-day PAST + 7-day FORECAST tables for:
# (1) Precipitation (2) Wind (3) Soil Moisture (API-based)

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

RADAR_IFRAME = r'''
<div class="radar-container" style="height: 100%;">
  <iframe width="100%" height="700"
    src="https://embed.windy.com/embed2.html?lat=35.726&lon=-77.916&detailLat=35.726&detailLon=-77.916&width=300&height=700&zoom=10&level=surface&overlay=radar&product=ecmwf&menu=&message=&marker=true&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=mph&metricTemp=%C2%B0F&radarRange=-1"
    frameborder="0"></iframe>
</div>
'''

st.set_page_config(
    page_title="Wayne Brothers - J&J Wilson NC",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# STYLING
# =========================
def apply_professional_styling():
    bg_url = "https://raw.githubusercontent.com/mickeybhenson-commits/J-J-LMDS-WILSON-NC/main/image_12e160.png"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        .stApp:before {{
            content: "";
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, rgba(0,0,0,0.90), rgba(20,20,30,0.88));
            pointer-events: none;
            z-index: 0;
        }}
        section.main, header, footer, [data-testid="stSidebar"] {{
            position: relative; z-index: 1;
        }}
        h1, h2, h3, h4 {{ color: #fff !important; text-shadow: 2px 2px 4px rgba(0,0,0,.45); }}
        p, span, div, label, li {{ color: #fff !important; }}
        .status-badge {{
            display:inline-block; padding:10px 16px; border-radius:8px; font-weight:800;
            box-shadow:0 2px 6px rgba(0,0,0,.35);
        }}
        .status-optimal{{background:#0B8A1D;color:#fff}}
        .status-saturated{{background:#FFAA00;color:#000}}
        .status-critical{{background:#FF6600;color:#fff}}
        .status-restricted{{background:#B00000;color:#fff}}
        .alert-box {{
            padding:14px; border-radius:10px; margin:10px 0; font-weight:650;
            background: rgba(30,30,35,.65); box-shadow:0 2px 6px rgba(0,0,0,.35);
        }}
        .alert-danger{{border-left:6px solid #CC0000;color:#FFD6D6}}
        .alert-warning{{border-left:6px solid #FFAA00;color:#FFE9C6}}
        .radar-container{{background:rgba(20,20,25,.9); border-radius:10px; padding:10px}}
        .section-divider{{border-top:2px solid rgba(255,255,255,.18); margin:18px 0}}
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_professional_styling()

# =========================
# HELPERS
# =========================
def safe_get(d: dict, path: list, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur

def first_list(site: dict, candidates: list) -> list | None:
    """
    Return the first candidate found that is a list (or tuple) of numeric-ish values.
    candidates: list of key-paths, each a list[str]
    """
    for p in candidates:
        v = safe_get(site, p, None)
        if isinstance(v, (list, tuple)) and len(v) > 0:
            return list(v)
    return None

def normalize_date_series(dates: pd.Series) -> pd.Series:
    return pd.to_datetime(dates, errors="coerce").dt.date

@st.cache_data(show_spinner=False)
def load_site_data(p: Path) -> dict:
    if not p.exists():
        raise FileNotFoundError(f"Site data not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def load_history(p: Path) -> pd.DataFrame:
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
    return df

def calculate_api(df: pd.DataFrame, days=5, decay=0.85) -> float:
    if df is None or df.empty or "precip_actual" not in df.columns:
        return 0.0
    recent = df.tail(days)["precip_actual"].fillna(0).astype(float).tolist()
    return round(sum(r * (decay ** i) for i, r in enumerate(reversed(recent))), 3)

def compute_api_series(history: pd.DataFrame, window_days=5, decay=0.85) -> pd.Series:
    """
    Compute API per row using the previous `window_days` precip values ending on that row.
    Returns a Series aligned to history index.
    """
    if history.empty or "precip_actual" not in history.columns:
        return pd.Series(dtype=float)

    precip = history["precip_actual"].fillna(0).astype(float).tolist()
    api_vals = []
    for idx in range(len(precip)):
        start = max(0, idx - (window_days - 1))
        chunk = precip[start:idx + 1]
        # most recent gets decay^0
        api = 0.0
        for i, r in enumerate(reversed(chunk)):
            api += r * (decay ** i)
        api_vals.append(round(api, 3))
    return pd.Series(api_vals, index=history.index, dtype=float)

def project_api_forecast(current_api: float, forecast_precip: list, decay=0.85) -> list:
    """
    Very simple API projection:
      API_next = decay * API_prev + precip_next
    This is a standard recursive API form (approximation).
    """
    api = float(current_api or 0.0)
    out = []
    for p in forecast_precip:
        try:
            p = float(p)
        except Exception:
            p = 0.0
        api = round((decay * api) + p, 3)
        out.append(api)
    return out

class WorkabilityAnalyzer:
    THRESHOLDS = {"optimal": 0.30, "saturated": 0.60, "critical": 0.85}
    @classmethod
    def assess(cls, api: float):
        if api < cls.THRESHOLDS["optimal"]:
            return "OPTIMAL", ["Full operations authorized","All earthwork permitted","Minimal restrictions"]
        if api < cls.THRESHOLDS["saturated"]:
            return "SATURATED", ["Monitor soils","Limit heavy equipment in low areas","Increase stabilization"]
        if api < cls.THRESHOLDS["critical"]:
            return "CRITICAL", ["Restrict grading","Implement erosion controls","Daily soil checks"]
        return "RESTRICTED", ["STOP earthwork","Emergency erosion only","Contact project engineer"]

def generate_alerts(site, api, status):
    alerts=[]
    gust = safe_get(site,["crane_safety","max_gust"],0)
    strikes = safe_get(site,["lightning","recent_strikes_50mi"],0)
    basin = safe_get(site,["swppp","sb3_capacity_pct"],0)
    if gust and float(gust)>25:
        alerts.append(("danger","WIND ALERT",f"Peak gusts {gust} MPH exceed 25 MPH. Suspend lifts."))
    if strikes and int(strikes)>0:
        alerts.append(("warning","LIGHTNING DETECTED",f"{strikes} strikes within 50 miles. Prepare protocols."))
    if status=="RESTRICTED":
        alerts.append(("danger","SOIL RESTRICTED",f"API {round(api,2)} — cease grading."))
    elif status=="CRITICAL":
        alerts.append(("warning","SOIL CRITICAL",f"API {round(api,2)} — minimize earthwork."))
    if basin and float(basin)>80:
        alerts.append(("warning","BASIN CAPACITY",f"SB3 at {basin}% — plan pump-out."))
    return alerts

def display_alerts(alerts):
    if not alerts:
        st.success("No active alerts — all systems nominal.")
        return
    for lvl,t,m in alerts:
        css="alert-danger" if lvl=="danger" else "alert-warning"
        st.markdown(f'<div class="alert-box {css}"><strong>{t}</strong><br>{m}</div>',unsafe_allow_html=True)

def render_table(title: str, df: pd.DataFrame):
    st.markdown(f"**{title}**")
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# MAIN
# =========================
def main():
    with st.sidebar:
        st.markdown("### SYSTEM CONTROLS")
        auto = st.checkbox("Auto-Refresh", False)
        sec = st.slider("Refresh Interval (seconds)",10,300,30)
        st.markdown("---")
        st.write(f"**Server Time:** {dt.datetime.now():%Y-%m-%d %H:%M:%S}")
        if st.button("Clear Cache"):
            st.cache_data.clear(); st.rerun()

    if auto:
        st.markdown(f"<meta http-equiv='refresh' content='{sec}'>", unsafe_allow_html=True)

    try:
        site = load_site_data(SITE_FILE)
        hist = load_history(HISTORY_FILE)
    except Exception as e:
        st.error(str(e)); st.stop()

    api_now = calculate_api(hist)
    status, recs = WorkabilityAnalyzer.assess(api_now)
    alerts = generate_alerts(site, api_now, status)

    c1,c2 = st.columns([3,1])
    with c1:
        st.title(APP_TITLE)
        st.caption(f"Last Updated: {site.get('last_updated','Unknown')} | API: {api_now}")
    with c2:
        st.markdown(f'<div class="status-badge status-{status.lower()}">SITE STATUS: {status}</div>',unsafe_allow_html=True)

    with st.expander("ACTIVE ALERTS & NOTIFICATIONS", expanded=bool(alerts)):
        display_alerts(alerts)

    tab_weather, tab_grading, tab_swppp, tab_crane, tab_analytics = st.tabs(
        ["Weather","Grading","SWPPP","Crane","Analytics"]
    )

    # =========================
    # WEATHER TAB — ADD TABLES
    # =========================
    with tab_weather:
        st.header("Meteorological Intelligence")
        left, right = st.columns([3,1])

        with left:
            st.subheader("Current Conditions")

            a24 = safe_get(site,["precipitation","actual_24h"],0)
            fp  = safe_get(site,["precipitation","forecast_prob"],0)
            strikes = safe_get(site,["lightning","recent_strikes_50mi"],0)
            lf = safe_get(site,["lightning","forecast"],"Unknown")

            r=st.columns(3)
            r[0].metric("24-Hour Precipitation", f"{a24} IN", delta=f"{fp}% forecast")
            r[1].metric("Lightning (50mi)", strikes, delta=str(lf))
            r[2].metric("Soil Saturation (API)", round(api_now,2), delta=status)

            st.markdown('<div class="section-divider"></div>',unsafe_allow_html=True)

            # --------- 7-DAY TABLES (PAST + FORECAST) ---------
            st.subheader("7-Day Tables (Past & Forecast)")

            # Build past 7-day data
            past = pd.DataFrame()
            if not hist.empty and "date" in hist.columns:
                tmp = hist.copy()
                tmp["day"] = normalize_date_series(tmp["date"])
                # If you have sub-daily data, aggregate to daily
                agg = {"precip_actual": "sum"}
                # Optional wind columns if present:
                if "wind_speed_mph" in tmp.columns:
                    agg["wind_speed_mph"] = "mean"
                if "wind_gust_mph" in tmp.columns:
                    agg["wind_gust_mph"] = "max"
                daily = tmp.groupby("day", as_index=False).agg(agg).sort_values("day")
                daily = daily.tail(7).reset_index(drop=True)

                # Compute API per day using cumulative history up to that day
                # (uses full history order; robust for daily table)
                hist_sorted = hist.sort_values("date").reset_index(drop=True)
                hist_sorted["day"] = normalize_date_series(hist_sorted["date"])
                api_series = compute_api_series(hist_sorted, window_days=5, decay=0.85)
                hist_sorted["api"] = api_series
                api_daily = (
                    hist_sorted.groupby("day", as_index=False)["api"]
                    .last()
                    .sort_values("day")
                )
                api_daily = api_daily.tail(7).reset_index(drop=True)

                past = daily.merge(api_daily, on="day", how="left")
            else:
                past = pd.DataFrame()

            # Pull forecast lists from site_status.json (supports multiple possible key paths)
            # You can store these in site_status.json as arrays like:
            #   "forecast": {"days": ["2026-01-01", ...], "precip_in": [...], "wind_mph": [...], "gust_mph": [...]}
            # or similar.
            f_days = first_list(site, [
                ["forecast", "days"], ["forecast_7d", "days"], ["forecast", "dates"], ["forecast_7d", "dates"]
            ])
            f_precip = first_list(site, [
                ["forecast", "precip_in"], ["forecast", "precip"], ["forecast_7d", "precip_in"], ["forecast_7d", "precip"],
                ["precipitation", "forecast_7d_in"], ["precipitation", "forecast_7d"]
            ])
            f_wind = first_list(site, [
                ["forecast", "wind_mph"], ["forecast", "wind_speed_mph"], ["forecast_7d", "wind_mph"], ["forecast_7d", "wind_speed_mph"]
            ])
            f_gust = first_list(site, [
                ["forecast", "gust_mph"], ["forecast", "wind_gust_mph"], ["forecast_7d", "gust_mph"], ["forecast_7d", "wind_gust_mph"]
            ])

            # Build forecast 7-day table
            forecast = pd.DataFrame()
            if f_precip is not None or f_wind is not None or f_gust is not None:
                n = 7
                def pad(lst):
                    if lst is None: return [None]*n
                    lst = list(lst)[:n]
                    return lst + [None]*(n - len(lst))

                days_col = pad(f_days)
                # If days list missing, synthesize dates
                if all(x is None for x in days_col):
                    start = dt.date.today()
                    days_col = [(start + dt.timedelta(days=i)).isoformat() for i in range(n)]

                forecast_precip = pad(f_precip)
                forecast_wind = pad(f_wind)
                forecast_gust = pad(f_gust)

                # Soil moisture forecast via API projection if precip forecast is present
                if f_precip is not None:
                    api_fc = project_api_forecast(api_now, forecast_precip, decay=0.85)
                else:
                    api_fc = [None]*n

                forecast = pd.DataFrame({
                    "day": days_col,
                    "precip_in": forecast_precip,
                    "wind_mph": forecast_wind,
                    "gust_mph": forecast_gust,
                    "api_projected": api_fc
                })
            else:
                forecast = pd.DataFrame()

            past_tab, forecast_tab = st.tabs(["Previous 7 Days", "Next 7 Days (Forecast)"])

            with past_tab:
                if past.empty:
                    st.warning("No usable history found. Ensure history.csv contains at least: date, precip_actual. Optional: wind_speed_mph, wind_gust_mph.")
                else:
                    # 1) Precip table
                    if "precip_actual" in past.columns:
                        render_table(
                            "Precipitation (Past 7 Days)",
                            past[["day", "precip_actual"]].rename(columns={"precip_actual": "precip_in"})
                        )
                    else:
                        st.info("History missing 'precip_actual' for past precipitation table.")

                    # 2) Wind table
                    wind_cols = ["day"]
                    if "wind_speed_mph" in past.columns: wind_cols.append("wind_speed_mph")
                    if "wind_gust_mph" in past.columns: wind_cols.append("wind_gust_mph")
                    if len(wind_cols) > 1:
                        render_table("Wind (Past 7 Days)", past[wind_cols])
                    else:
                        st.info("Add optional history columns for wind: 'wind_speed_mph' and/or 'wind_gust_mph' to show past wind table.")

                    # 3) Soil moisture table (API)
                    if "api" in past.columns:
                        render_table("Soil Moisture Proxy (API) — Past 7 Days", past[["day", "api"]])
                    else:
                        st.info("API could not be computed for past table (requires 'precip_actual').")

            with forecast_tab:
                if forecast.empty:
                    st.warning(
                        "No forecast arrays found in site_status.json.\n\n"
                        "To enable these tables, add arrays under something like:\n"
                        "forecast: { days: [...], precip_in: [...], wind_mph: [...], gust_mph: [...] }"
                    )
                else:
                    # 1) Precip forecast
                    if "precip_in" in forecast.columns:
                        render_table("Precipitation (Next 7 Days Forecast)", forecast[["day", "precip_in"]])
                    # 2) Wind forecast
                    wind_fc_cols = ["day"]
                    if "wind_mph" in forecast.columns: wind_fc_cols.append("wind_mph")
                    if "gust_mph" in forecast.columns: wind_fc_cols.append("gust_mph")
                    if len(wind_fc_cols) > 1:
                        render_table("Wind (Next 7 Days Forecast)", forecast[wind_fc_cols])
                    # 3) Soil moisture forecast (API projection)
                    if "api_projected" in forecast.columns:
                        render_table("Soil Moisture Proxy (Projected API) — Next 7 Days", forecast[["day", "api_projected"]])

            st.markdown('<div class="section-divider"></div>',unsafe_allow_html=True)

            st.subheader("Forecast & Analysis")
            cA,cB=st.columns(2)
            with cA:
                st.write(f"**Precip Probability:** {fp}%")
                st.write(f"**24h Actual:** {a24} IN")
            with cB:
                st.write(f"**Lightning Status:** {lf}")
                st.write(f"**Recent Strikes:** {strikes}")

        with right:
            st.markdown("**Live Radar — Wilson, NC**")
            st.components.v1.html(RADAR_IFRAME, height=720)

    # =========================
    # GRADING
    # =========================
    with tab_grading:
        st.header("Grading Operations & Soil Workability")
        l,r = st.columns([2,3])
        with l:
            st.markdown(f'<div class="status-badge status-{status.lower()}" style="font-size:1.3em;">{status}</div>',unsafe_allow_html=True)
            st.metric("API", api_now)
            st.progress(min(api_now,1.0))
            st.markdown("**API Thresholds:**")
            st.write(f"Optimal: < {WorkabilityAnalyzer.THRESHOLDS['optimal']}")
            st.write(f"Saturated: < {WorkabilityAnalyzer.THRESHOLDS['saturated']}")
            st.write(f"Critical: < {WorkabilityAnalyzer.THRESHOLDS['critical']}")
            st.write(f"Restricted: ≥ {WorkabilityAnalyzer.THRESHOLDS['critical']}")
        with r:
            st.subheader("Operational Recommendations")
            for i,x in enumerate(recs,1): st.info(f"**{i}.** {x}")
            with st.expander("About API Calculation"):
                st.markdown(
                    "**API** is a weighted measure of recent rainfall indicating soil moisture:\n\n"
                    "```\n"
                    "API = Σ (Rainfall_i × 0.85^i)\n"
                    "```\n\n"
                    "where `i` is the number of days ago (most recent rain has the highest weight)."
                )

    # =========================
    # SWPPP
    # =========================
    with tab_swppp:
        st.header("Environmental & SWPPP Compliance")
        c1,c2=st.columns(2)
        with c1:
            cap=safe_get(site,["swppp","sb3_capacity_pct"],0)
            fb=safe_get(site,["swppp","freeboard_feet"],"—")
            st.metric("SB3 Capacity", f"{cap}%"); st.metric("Freeboard", f"{fb} FT")
            try:
                st.progress(min(float(cap)/100 if cap else 0,1))
            except Exception:
                st.progress(0.0)
        with c2:
            st.metric("Disturbed Acres", safe_get(site,["swppp","disturbed_acres"],"—"))
            st.write(f"**Silt Fence:** {safe_get(site,['swppp','silt_fence_integrity'],'—')}")
        with st.expander("Daily Inspection Checklist"):
            st.checkbox("Basin freeboard adequate (>1.0 ft)", value=True)
            st.checkbox("Silt fence integrity maintained", value=True)
            st.checkbox("Inlet protection in place", value=True)
            st.checkbox("No off-site sediment discharge", value=True)
            st.checkbox("Stabilized areas maintained", value=True)

    # =========================
    # CRANE
    # =========================
    with tab_crane:
        st.header("Crane & Lift Operations Safety")
        a,b,c=st.columns(3)
        gust=safe_get(site,["crane_safety","max_gust"],0)
        wind=safe_get(site,["crane_safety","wind_speed"],0)
        with a:
            st.subheader("Wind")
            st.metric("Wind Speed", f"{wind} MPH")
            st.metric("Max Gust", f"{gust} MPH")
            try:
                g=float(gust)
            except Exception:
                g=0.0
            st.success("Safe") if g<20 else st.warning("Monitor") if g<25 else st.error("Suspend")
        with b:
            st.subheader("Lightning")
            st.write(f"**Threat:** {safe_get(site,['lightning','forecast'],'—')}")
            st.write(f"**Recent Strikes (50mi):** {safe_get(site,['lightning','recent_strikes_50mi'],0)}")
        with c:
            st.subheader("Ground")
            st.write(f"**Soil Workability:** {status}")
            st.write(f"**API:** {round(api_now,2)}")

    # =========================
    # ANALYTICS
    # =========================
    with tab_analytics:
        st.header("Historical Analytics & Trends")
        if hist.empty:
            st.warning("No historical data.")
        else:
            days=st.slider("Days",7,30,14)
            recent=hist.tail(days)
            if {"date","precip_actual"}<=set(recent.columns):
                st.line_chart(recent.set_index("date")["precip_actual"])

    st.markdown("---")
    f1,f2,f3=st.columns(3)
    f1.caption("Contractor Defense Portal v2.2")
    f2.caption("Powered by Real-Time Environmental Monitoring")
    f3.caption(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}")

if __name__=="__main__":
    main()

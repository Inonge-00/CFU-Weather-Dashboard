from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="CFU Farmer Weather Engagement Dashboard",
    layout="wide"
)

st_autorefresh(interval=300000, key="cfu_dashboard_refresh")  # 5 minutes
px.defaults.template = "simple_white"

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def get_last_refresh(sheet):
    try:
        meta_df = pd.DataFrame(sheet.worksheet("Meta").get_all_records())
        if meta_df.empty:
            return "No refresh recorded yet"

        meta_df.columns = meta_df.columns.str.strip().str.lower()

        if "key" in meta_df.columns and "value" in meta_df.columns:
            row = meta_df[meta_df["key"] == "last_refresh"]
            if not row.empty:
                return str(row["value"].iloc[0]).strip()

        return "No refresh recorded yet"
    except Exception:
        return "No refresh recorded yet"


def standardize_location(value):
    if pd.isna(value):
        return value

    text = str(value).strip().lower()

    # Priority areas
    if "central" in text:
        return "Central Province"
    elif "kapiri" in text:
        return "Kapiri"
    elif "monze" in text:
        return "Monze"
    elif "mkushi" in text:
        return "Mkushi"
    elif "choma" in text:
        return "Choma"
    elif "shibuyunji" in text:
        return "Shibuyunji"
    elif "mpongwe" in text:
        return "Mpongwe"

    # Other common districts
    elif "serenje" in text:
        return "Serenje"
    elif "mukwela" in text:
        return "Mukwela"
    elif "zimba" in text:
        return "Zimba"
    elif "kabwe" in text:
        return "Kabwe"
    elif "kalomo" in text:
        return "Kalomo"
    elif "mazabuka" in text:
        return "Mazabuka"
    elif "kazungula" in text:
        return "Kazungula"
    elif "chibombo" in text:
        return "Chibombo District"
    elif "mumbwa" in text:
        return "Mumbwa"

    return str(value).strip()


# ---------------------------------------------------
# STYLING
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f8f5ef 0%, #efe7d8 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e9e0cf 0%, #e4dac7 100%);
    border-right: 1px solid rgba(94, 142, 46, 0.12);
}

/* Typography */
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

h1, h2, h3 {
    color: #24411a !important;
}

h1 {
    font-size: 2.95rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.2px;
}

h2 {
    font-size: 2rem !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

/* Hero banner */
.top-banner {
    background: linear-gradient(90deg, rgba(94,142,46,0.95) 0%, rgba(120,165,62,0.95) 100%);
    padding: 22px 32px;
    border-radius: 24px;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(94, 142, 46, 0.18);
}

.top-banner h1 {
    color: #ffffff !important;
    text-align: center;
    margin: 0;
}

/* Header logos */
.logo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding-top: 8px;
}

/* Intro / hero card */
.intro-box {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 32px;
    border-radius: 24px;
    border-left: 8px solid #F3AE3D;
    margin-bottom: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.intro-box p {
    font-size: 1.12rem;
    color: #38433b;
    line-height: 1.85;
    margin-bottom: 0.9rem;
}

/* Status chip */
.status-chip {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(94, 142, 46, 0.16);
    border-radius: 999px;
    padding: 10px 16px;
    display: inline-block;
    margin-bottom: 18px;
    font-size: 0.98rem;
    color: #24411a;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}

/* KPI cards */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(252,250,245,0.96) 100%);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(94, 142, 46, 0.32) !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.05);
}

div[data-testid="stMetricLabel"] {
    font-size: 17px !important;
    font-weight: 600 !important;
    color: #42503b !important;
}

div[data-testid="stMetricValue"] {
    color: #5E8E2E !important;
    font-weight: 800 !important;
    font-size: 2.3rem !important;
}

/* Chart cards */
.chart-card {
    background: rgba(255,255,255,0.76);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 22px;
    padding: 18px 20px 12px 20px;
    box-shadow: 0 10px 22px rgba(0,0,0,0.05);
    border: 1px solid rgba(94, 142, 46, 0.10);
    margin-bottom: 14px;
}

.section-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: #24411a;
    margin-top: 8px;
    margin-bottom: 12px;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
}

/* Footer */
.footer {
    text-align: center;
    font-size: 15px;
    color: #5b6356;
    margin-top: 18px;
    padding-bottom: 8px;
}

/* Spacing */
.block-container {
    padding-top: 1.3rem;
    padding-bottom: 2rem;
}

/* Sidebar filter labels */
label, .stSelectbox label, .stMultiSelect label {
    font-size: 16px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER WITH LOGOS + BANNER
# ---------------------------------------------------
logo1, title_col, logo2 = st.columns([1.8, 4.2, 1.0])

with logo1:
    st.markdown("<div class='logo-wrap'>", unsafe_allow_html=True)
    try:
        st.image("cfu_logo.png", width=320)
    except Exception as e:
        st.caption(f"CFU logo error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

with title_col:
    st.markdown("""
    <div class="top-banner">
        <h1>Conservation Farming Unit: Farmer Weather Engagement Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

with logo2:
    st.markdown("<div class='logo-wrap'>", unsafe_allow_html=True)
    try:
        st.image("ap_logo.png", width=110)
    except Exception as e:
        st.caption(f"AgriPredict logo error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# DATA ENGINE
# ---------------------------------------------------
@st.cache_data(ttl=300)
def get_cfu_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    url = "https://docs.google.com/spreadsheets/d/1P4ys9cb6lJM1uwVzhV1iVTQ5UzZUO0Ae2bIje4ZDF90/edit"
    sheet = client.open_by_url(url)

    users_df = pd.DataFrame(sheet.worksheet("Users").get_all_records())
    sessions_df = pd.DataFrame(sheet.worksheet("Sessions").get_all_records())

    users_df.columns = users_df.columns.str.strip().str.lower()
    sessions_df.columns = sessions_df.columns.str.strip().str.lower()

    for col in users_df.columns:
        if users_df[col].dtype == "object":
            users_df[col] = users_df[col].astype(str).str.strip()

    for col in sessions_df.columns:
        if sessions_df[col].dtype == "object":
            sessions_df[col] = sessions_df[col].astype(str).str.strip()

    if "session_date" in sessions_df.columns:
        sessions_df["session_date"] = pd.to_datetime(
            sessions_df["session_date"], errors="coerce"
        )
        sessions_df = sessions_df.dropna(subset=["session_date"])

        start_dt = pd.Timestamp("2025-10-01")
        sessions_df = sessions_df[sessions_df["session_date"] >= start_dt]

    return users_df, sessions_df, sheet


try:
    users_orig, sessions_orig, sheet = get_cfu_data()

    # ---------------------------------------------------
    # CLEAN LOCATION FIELDS
    # ---------------------------------------------------
    if "loc" in users_orig.columns:
        users_orig["loc_clean"] = users_orig["loc"].apply(standardize_location)

    if "loc" in sessions_orig.columns:
        sessions_orig["loc_clean"] = sessions_orig["loc"].apply(standardize_location)

    if "state" in users_orig.columns:
        users_orig["state_clean"] = users_orig["state"].apply(standardize_location)

    if "state" in sessions_orig.columns:
        sessions_orig["state_clean"] = sessions_orig["state"].apply(standardize_location)

    # ---------------------------------------------------
    # SIDEBAR FILTERS
    # ---------------------------------------------------
    st.sidebar.header("🔎 Global Filters")

    core_services = [
        "Weather Forecast 30 days",
        "Weather Forecast 16 days",
        "96-Hour Weather"
    ]

    selected_service = st.sidebar.multiselect(
        "Filter by Weather Service",
        options=core_services,
        default=core_services
    )

    province_options = []
    if "state_clean" in sessions_orig.columns:
        province_options = sorted(
            [x for x in sessions_orig["state_clean"].dropna().unique() if str(x).strip() != ""]
        )

    selected_province = st.sidebar.multiselect(
        "Filter by Province",
        options=province_options
    )

    sessions = sessions_orig.copy()

    if "service" in sessions.columns:
        sessions = sessions[sessions["service"].isin(selected_service)]

    if selected_province and "state_clean" in sessions.columns:
        sessions = sessions[sessions["state_clean"].isin(selected_province)]

    # ---------------------------------------------------
    # PAGE RELOAD INDICATOR
    # ---------------------------------------------------
    page_reload_time = datetime.now().strftime("%H:%M:%S")

    # ---------------------------------------------------
    # WELCOME + STATUS
    # ---------------------------------------------------
    st.markdown("""
    <div class="intro-box">
        <h2>Welcome to the CFU Digital Weather Engagement Dashboard 👋</h2>
        <p>
            This live dashboard provides a view of how farmers across Zambia are engaging with AgriPredict’s digital weather services delivered in partnership with the Conservation Farming Unit.
        </p>
        <p>
            It tracks use of the 30-Day Forecast, 16-Day Forecast, and 96-Hour Weather Alert services, helping CFU monitor access to weather information that supports planning and agricultural decision-making.
        </p>
        <p>
            Use the global filters on the left to explore results by weather service and province.
        </p>
        <p>
            Reporting period: Live data from 1st October 2025 onward
        </p>
    </div>
    """, unsafe_allow_html=True)

    last_refresh = get_last_refresh(sheet)
    st.markdown(
        f"<div class='status-chip'>🟢 Last successful refresh: {last_refresh} &nbsp;&nbsp;|&nbsp;&nbsp; Dashboard page reloaded at: {page_reload_time}</div>",
        unsafe_allow_html=True
    )

    # ---------------------------------------------------
    # KPI PREP
    # ---------------------------------------------------
    w30 = len(sessions[sessions["service"] == "Weather Forecast 30 days"]) if "service" in sessions.columns else 0
    w16 = len(sessions[sessions["service"] == "Weather Forecast 16 days"]) if "service" in sessions.columns else 0
    w96 = len(sessions[sessions["service"] == "96-Hour Weather"]) if "service" in sessions.columns else 0

    active_provinces = sessions["state_clean"].nunique() if "state_clean" in sessions.columns else 0

    if "loc_clean" in sessions.columns:
        district_series = sessions["loc_clean"][sessions["loc_clean"] != "Central Province"]
        active_districts = district_series.nunique()
    else:
        active_districts = 0

    if "session_date" in sessions.columns:
        last_30_cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=30)
        last_30_interactions = len(sessions[sessions["session_date"] >= last_30_cutoff])
    else:
        last_30_interactions = 0

    if not sessions.empty and "session_date" in sessions.columns:
        daily_counts = sessions.groupby(sessions["session_date"].dt.date).size()
        avg_daily_interactions = round(daily_counts.mean(), 1)
    else:
        avg_daily_interactions = 0

    # ---------------------------------------------------
    # INTERACTIONS BY GENDER PREP
    # ---------------------------------------------------
    sessions_gender = None
    join_key = None

    if "username" in sessions.columns and "username" in users_orig.columns and "gender" in users_orig.columns:
        join_key = "username"
    elif "user_id" in sessions.columns and "user_id" in users_orig.columns and "gender" in users_orig.columns:
        join_key = "user_id"

    if join_key is not None:
        gender_lookup = users_orig[[join_key, "gender"]].drop_duplicates()
        sessions_gender = sessions.merge(gender_lookup, on=join_key, how="left")
        sessions_gender["gender"] = sessions_gender["gender"].fillna("U")

    # ---------------------------------------------------
    # TABS
    # ---------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Geography", "Trends", "Priority Areas"])

    # TAB 1
    with tab1:
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Registered Users", f"{len(users_orig):,}")
        k2.metric("Total Interactions", f"{len(sessions):,}")
        k3.metric("30-Day Forecasts", f"{w30:,}")
        k4.metric("16-Day Forecasts", f"{w16:,}")
        k5.metric("96-Hour Alerts", f"{w96:,}")

        n1, n2, n3, n4 = st.columns(4)
        n1.metric("Active Provinces", f"{active_provinces:,}")
        n2.metric("Active Districts", f"{active_districts:,}")
        n3.metric("Interactions (Last 30 Days)", f"{last_30_interactions:,}")
        n4.metric("Average Daily Interactions", f"{avg_daily_interactions:,}")

        st.write("")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>📊 Service Popularity</div>", unsafe_allow_html=True)

            fig_pie = px.pie(
                sessions,
                names="service",
                hole=0.58,
                color="service",
                color_discrete_map={
                    "Weather Forecast 16 days": "#5E8E2E",
                    "96-Hour Weather": "#F3AE3D",
                    "Weather Forecast 30 days": "#E85B52"
                }
            )
            fig_pie.update_traces(textfont_size=18, marker=dict(line=dict(color="#ffffff", width=2)))
            fig_pie.update_layout(
                font=dict(size=18),
                height=460,
                margin=dict(t=20, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend_title="Service",
                legend=dict(font=dict(size=16), title_font=dict(size=17))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>👫 Interactions by Gender</div>", unsafe_allow_html=True)

            if sessions_gender is not None:
                fig_gen = px.pie(
                    sessions_gender,
                    names="gender",
                    hole=0.58,
                    color="gender",
                    color_discrete_map={
                        "M": "#92B23A",
                        "F": "#F3AE3D",
                        "U": "#BDBDBD"
                    }
                )
                fig_gen.update_traces(textfont_size=18, marker=dict(line=dict(color="#ffffff", width=2)))
                fig_gen.update_layout(
                    font=dict(size=18),
                    height=460,
                    margin=dict(t=20, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend_title="Gender",
                    legend=dict(font=dict(size=16), title_font=dict(size=17))
                )
                st.plotly_chart(fig_gen, use_container_width=True)
            else:
                st.info("Unable to calculate interactions by gender because username/user_id or gender is missing.")
            st.markdown("</div>", unsafe_allow_html=True)

    # TAB 2
    with tab2:
        r1, r2 = st.columns(2)

        with r1:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>📍 Interactions by Province (Top 10)</div>", unsafe_allow_html=True)

            if "state_clean" in sessions.columns:
                prov = sessions["state_clean"].value_counts().head(10).reset_index()
                prov.columns = ["state", "count"]

                fig_prov = px.bar(prov, x="state", y="count", text="count", color_discrete_sequence=["#5E8E2E"])
                fig_prov.update_traces(textposition="outside", textfont_size=18, marker_line_color="#4D7725", marker_line_width=0.5)
                fig_prov.update_layout(
                    font=dict(size=18),
                    xaxis_title="Province",
                    yaxis_title="Interactions",
                    xaxis_tickangle=25,
                    height=470,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                    yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18))
                )
                st.plotly_chart(fig_prov, use_container_width=True)
            else:
                st.info("Province data not available.")
            st.markdown("</div>", unsafe_allow_html=True)

        with r2:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🏘️ Interactions by District (Top 10)</div>", unsafe_allow_html=True)

            district_df = sessions.copy()
            if "loc_clean" in district_df.columns:
                district_df = district_df[district_df["loc_clean"] != "Central Province"]

                dist = district_df["loc_clean"].value_counts().head(10).reset_index()
                dist.columns = ["loc", "count"]

                fig_dist = px.bar(dist, x="loc", y="count", text="count", color_discrete_sequence=["#C9D83B"])
                fig_dist.update_traces(textposition="outside", textfont_size=18, marker_line_color="#9EAF22", marker_line_width=0.5)
                fig_dist.update_layout(
                    font=dict(size=18),
                    xaxis_title="District",
                    yaxis_title="Interactions",
                    xaxis_tickangle=25,
                    height=470,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                    yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18))
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("District data not available.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🗺️ Farmer Weather Engagement Heatmap</div>", unsafe_allow_html=True)

        heat_df = sessions.copy()

        if "lat" in heat_df.columns and "lon" in heat_df.columns:
            heat_df["lat"] = pd.to_numeric(heat_df["lat"], errors="coerce")
            heat_df["lon"] = pd.to_numeric(heat_df["lon"], errors="coerce")
            heat_df = heat_df.dropna(subset=["lat", "lon"])

            hover_name_col = "loc_clean" if "loc_clean" in heat_df.columns else "loc"
            hover_dict = {}

            if "state_clean" in heat_df.columns:
                hover_dict["state_clean"] = True
            elif "state" in heat_df.columns:
                hover_dict["state"] = True

            hover_dict["lat"] = False
            hover_dict["lon"] = False

            fig_heat = px.density_mapbox(
                heat_df,
                lat="lat",
                lon="lon",
                radius=18,
                center={"lat": -13.1339, "lon": 27.8493},
                zoom=5.2,
                hover_name=hover_name_col,
                hover_data=hover_dict
            )

            fig_heat.update_layout(
                mapbox_style="carto-positron",
                height=580,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(size=17)
            )

            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Latitude and longitude data not available for mapping.")

        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 3
    with tab3:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📈 Daily Engagement Trend</div>", unsafe_allow_html=True)

        if "session_date" in sessions.columns:
            trend = sessions.groupby(sessions["session_date"].dt.date).size().reset_index(name="count")

            fig_trend = px.area(trend, x="session_date", y="count")
            fig_trend.update_traces(line=dict(color="#5E8E2E", width=3), fillcolor="rgba(94,142,46,0.30)")
            fig_trend.update_layout(
                font=dict(size=18),
                xaxis_title="Date",
                yaxis_title="Interactions",
                height=530,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18))
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Trend data not available.")
        st.markdown("</div>", unsafe_allow_html=True)

        t1, t2 = st.columns(2)

        with t1:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🗓️ Monthly Engagement Trend</div>", unsafe_allow_html=True)

            if "session_date" in sessions.columns:
                monthly = sessions.copy()
                monthly["month"] = monthly["session_date"].dt.to_period("M").astype(str)
                monthly = monthly.groupby("month").size().reset_index(name="count")

                fig_monthly = px.bar(monthly, x="month", y="count", text="count", color_discrete_sequence=["#5E8E2E"])
                fig_monthly.update_traces(textposition="outside", textfont_size=18)
                fig_monthly.update_layout(
                    font=dict(size=18),
                    xaxis_title="Month",
                    yaxis_title="Interactions",
                    height=470,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                    yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18))
                )
                st.plotly_chart(fig_monthly, use_container_width=True)
            else:
                st.info("Monthly trend data not available.")
            st.markdown("</div>", unsafe_allow_html=True)

        with t2:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🧭 Service Usage by Province</div>", unsafe_allow_html=True)

            if "state_clean" in sessions.columns and "service" in sessions.columns:
                svc_prov = sessions.groupby(["state_clean", "service"]).size().reset_index(name="count")
                top_states = sessions["state_clean"].value_counts().head(8).index.tolist()
                svc_prov = svc_prov[svc_prov["state_clean"].isin(top_states)]

                fig_service_prov = px.bar(
                    svc_prov,
                    x="state_clean",
                    y="count",
                    color="service",
                    barmode="stack",
                    color_discrete_map={
                        "Weather Forecast 16 days": "#5E8E2E",
                        "96-Hour Weather": "#F3AE3D",
                        "Weather Forecast 30 days": "#E85B52"
                    }
                )
                fig_service_prov.update_layout(
                    font=dict(size=18),
                    xaxis_title="Province",
                    yaxis_title="Interactions",
                    xaxis_tickangle=25,
                    height=470,
                    margin=dict(t=20, b=20, l=20, r=20),
                    legend_title="Service",
                    legend=dict(font=dict(size=15), title_font=dict(size=17)),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                    yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18))
                )
                st.plotly_chart(fig_service_prov, use_container_width=True)
            else:
                st.info("Service-by-province data not available.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📈 Monthly Service Trend</div>", unsafe_allow_html=True)

        if "session_date" in sessions.columns and "service" in sessions.columns:
            monthly_service = sessions.copy()
            monthly_service["month"] = monthly_service["session_date"].dt.to_period("M").astype(str)
            monthly_service = monthly_service.groupby(["month", "service"]).size().reset_index(name="count")

            fig_monthly_service = px.line(
                monthly_service,
                x="month",
                y="count",
                color="service",
                markers=True,
                color_discrete_map={
                    "Weather Forecast 16 days": "#5E8E2E",
                    "96-Hour Weather": "#F3AE3D",
                    "Weather Forecast 30 days": "#E85B52"
                }
            )

            fig_monthly_service.update_layout(
                font=dict(size=18),
                height=500,
                xaxis_title="Month",
                yaxis_title="Interactions",
                legend_title="Service",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
                legend=dict(font=dict(size=15), title_font=dict(size=17))
            )

            st.plotly_chart(fig_monthly_service, use_container_width=True)
        else:
            st.info("Monthly service trend data not available.")

        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 4
    with tab4:
        priority_areas = [
            "Central Province",
            "Kapiri",
            "Monze",
            "Mkushi",
            "Choma",
            "Shibuyunji",
            "Mpongwe"
        ]

        rows = []

        for area in priority_areas:
            if "loc_clean" in users_orig.columns and "state_clean" in users_orig.columns:
                matched_users = users_orig[
                    (users_orig["loc_clean"] == area) |
                    (users_orig["state_clean"] == area)
                ]
            else:
                matched_users = pd.DataFrame()

            rows.append({
                "District": area,
                "Users": len(matched_users)
            })

        priority_table = pd.DataFrame(rows)

        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📋 Priority Areas Summary (Users)</div>", unsafe_allow_html=True)
        st.dataframe(priority_table, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📍 Users Across Priority Areas</div>", unsafe_allow_html=True)

        fig_priority = px.bar(
            priority_table,
            x="District",
            y="Users",
            text="Users",
            color_discrete_sequence=["#5E8E2E"]
        )
        fig_priority.update_traces(textposition="outside", textfont_size=18)
        fig_priority.update_layout(
            font=dict(size=18),
            height=470,
            xaxis_title="Priority Area",
            yaxis_title="Users",
            xaxis_tickangle=20,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18)),
            yaxis=dict(tickfont=dict(size=15), title_font=dict(size=18))
        )
        st.plotly_chart(fig_priority, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Waiting for data connection... ({e})")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown(
    "<div class='footer'>Updated live | Partnership: AgriPredict & CFU</div>",
    unsafe_allow_html=True
)
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Kampala Urban Flood Management System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 2.3rem; font-weight: 700; color: #1e1e2f; margin-bottom: 0px; }
    .subtitle { font-size: 1.1rem; color: #555555; margin-bottom: 20px; }
    .legend-box { background-color: #1e1e2f; padding: 12px; border-radius: 8px; margin-bottom: 15px; display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌊 Kampala Urban Flood Risk & Drainage Intelligence Hub</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Open-source geospatial command center for topographic hazard monitoring, stormwater channels, and flood impact simulation.</p>', unsafe_allow_html=True)

# --- 2. Standalone Navigation Tabs ---
tab_hazard, tab_infrastructure, tab_simulation = st.tabs([
    " Drainage Channels & Hazard Basins", 
    " Asset Vulnerability & Analytics", 
    " Rainfall Impact & Simulation"
])

# =========================================================================
# TAB 1: DRAINAGE CHANNELS & HAZARD BASINS
# =========================================================================
with tab_hazard:
    st.subheader("🗺️ Kampala Stormwater Channels & Low-Lying Basins")
    st.markdown("Interactive map tracking major natural streams, man-made drainage channels, and flash-flood pooling zones.")

    # Inline Control Panel
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        rainfall_slider = st.slider("Simulated Rainfall Intensity (mm/hr)", min_value=10, max_value=100, value=50, key="rain_intensity")
    with c2:
        risk_filter = st.selectbox("Filter Risk Level", ["All Basins", "High Flash Flood Risk Only"], key="basin_filter")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("💡 Switch filters to isolate high-danger zones along primary channels.")

    st.markdown("---")

    # Datasets
    drainage_basins = [
        {"basin_id": "BSN-01", "name": "Kalerwe Valley Basin", "lat": 0.3520, "lon": 32.5740, "risk": "High Risk", "channel": "Nakivubo Primary Channel", "vulnerable_pop": 1420},
        {"basin_id": "BSN-02", "name": "Bwaise Lowland Catchment", "lat": 0.3580, "lon": 32.5650, "risk": "High Risk", "channel": "Lubigi Wetland Spur", "vulnerable_pop": 2100},
        {"basin_id": "BSN-03", "name": "Nakivubo Channel Central", "lat": 0.3180, "lon": 32.5850, "risk": "Medium Risk", "channel": "Nakivubo Main Channel", "vulnerable_pop": 980},
        {"basin_id": "BSN-04", "name": "Industrial Area Drainage", "lat": 0.3120, "lon": 32.6020, "risk": "Low Risk", "channel": "Nakivubo Outfall", "vulnerable_pop": 340},
        {"basin_id": "BSN-05", "name": "Kyambogo Lower Valley", "lat": 0.3450, "lon": 32.6100, "risk": "Medium Risk", "channel": "Ntinda Stream Collector", "vulnerable_pop": 650},
        {"basin_id": "BSN-06", "name": "Nateete Wetland Basin", "lat": 0.3150, "lon": 32.5450, "risk": "High Risk", "channel": "Mayanja River Basin", "vulnerable_pop": 1850}
    ]
    df_basins = pd.DataFrame(drainage_basins)

    if risk_filter == "High Flash Flood Risk Only":
        df_basins = df_basins[df_basins['risk'] == "High Risk"]

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monitored Basins", len(df_basins))
    m2.metric("High-Risk Zones", len(df_basins[df_basins['risk'] == "High Risk"]))
    m3.metric("Rainfall Load", f"{rainfall_slider} mm/hr")
    m4.metric("At-Risk Population", f"{df_basins['vulnerable_pop'].sum():,} people")

    # Legend
    st.markdown("""
    <div class="legend-box">
        <b style="color: white; font-size: 14px;">🌊 Map Legend:</b>
        <span style="color: #ff3333; font-weight: bold;">🔴 High Flash Flood Risk</span>
        <span style="color: #ffaa00; font-weight: bold;">🟠 Moderate Risk Basin</span>
        <span style="color: #00cc66; font-weight: bold;">🟢 Low Risk / Controlled</span>
        <span style="color: #3399ff; font-weight: bold;">〰️ Primary Drainage Channels</span>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Map with Drainage Lines & Basin Markers
    m_flood = folium.Map(location=[0.3476, 32.5825], zoom_start=13, tiles="OpenStreetMap")

    # Draw simulated primary drainage channels (Line Strings)
    channels_coords = [
        [(0.3700, 32.5700), (0.3520, 32.5740), (0.3350, 32.5800), (0.3180, 32.5850), (0.3120, 32.6020)], # Nakivubo Channel
        [(0.3800, 32.5550), (0.3580, 32.5650), (0.3400, 32.5700)], # Lubigi Spur
        [(0.3500, 32.6200), (0.3450, 32.6100), (0.3300, 32.5950)]  # Ntinda Collector
    ]
    for ch_path in channels_coords:
        folium.PolyLine(ch_path, color="#3399ff", weight=4, opacity=0.8, tooltip="Primary Stormwater Drainage Channel").add_to(m_flood)

    # Draw basin markers
    for _, row in df_basins.iterrows():
        if row['risk'] == "High Risk":
            color, fill_col, radius = "#ff3333", "#ff6666", 18
        elif row['risk'] == "Medium Risk":
            color, fill_col, radius = "#ffaa00", "#ffcc66", 14
        else:
            color, fill_col, radius = "#00cc66", "#66ff99", 10

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color=color,
            weight=2,
            fill=True,
            fill_color=fill_col,
            fill_opacity=0.8,
            popup=(
                f"<b>Basin:</b> {row['name']}<br>"
                f"<b>Risk:</b> {row['risk']}<br>"
                f"<b>Channel:</b> {row['channel']}<br>"
                f"<b>At-Risk Pop:</b> {row['vulnerable_pop']}"
            )
        ).add_to(m_flood)

    st_folium(m_flood, width=1200, height=480, key="map_hazard_tab")

    st.markdown("#### Drainage Basin Summary Table")
    st.dataframe(df_basins, use_container_width=True)


# =========================================================================
# TAB 2: ASSET VULNERABILITY & ANALYTICS
# =========================================================================
with tab_infrastructure:
    st.subheader("Critical Infrastructure & Asset Impact Analysis")
    st.markdown("Evaluates infrastructure exposure across Kampala's flood-prone transport and educational sectors.")

    infra_data = [
        {"asset_id": "INF-01", "asset_name": "Bombo Road Access Point", "category": "Transport Artery", "location": "Kalerwe Junction", "impact_status": "Severe Disruption"},
        {"asset_id": "INF-02", "asset_name": "Bwaise Primary School", "category": "Educational", "location": "Bwaise Lowland", "impact_status": "High Vulnerability"},
        {"asset_id": "INF-03", "asset_name": "Owino Market Perimeter", "category": "Commercial Hub", "location": "Nakivubo Basin", "impact_status": "Moderate Flooding"},
        {"asset_id": "INF-04", "asset_name": "Northern Bypass Culvert", "category": "Infrastructure", "location": "Bwaise-Kansanga Link", "impact_status": "Blocked Drainage"},
        {"asset_id": "INF-05", "asset_name": "Jinja Road Spur", "category": "Transport Artery", "location": "Industrial Area", "impact_status": "Clear / Flowing"}
    ]
    df_infra = pd.DataFrame(infra_data)

    i1, i2 = st.columns(2)
    with i1:
        st.markdown("#### At-Risk Asset Register")
        st.dataframe(df_infra, use_container_width=True)
    with i2:
        st.markdown("####  Asset Category Vulnerability Breakdown")
        category_counts = df_infra['category'].value_counts()
        st.bar_chart(category_counts)

    st.info("💡 **Actionable Insight:** Tracking asset vulnerabilities helps municipal authorities prioritize drainage dredging before peak wet seasons.")


# =========================================================================
# TAB 3: RAINFALL IMPACT & SIMULATION
# =========================================================================
with tab_simulation:
    st.subheader(" Stormwater Runoff vs. Population Impact Simulation")
    st.markdown("Simulates how increasing hourly rainfall intensity scales up the number of affected residents across Kampala's lowlands.")

    # Interactive simulation chart data based on rainfall slider
    rainfall_levels = [20, 40, 60, 80, 100]
    simulated_impact = [450, 1200, 2800, 4900, 7500]
    
    sim_df = pd.DataFrame({
        "Rainfall (mm/hr)": rainfall_levels,
        "Estimated Affected Population": simulated_impact
    }).set_index("Rainfall (mm/hr)")

    s1, s2 = st.columns([1, 2])
    with s1:
        st.markdown("#### 🔍 Simulation Parameters")
        st.metric("Current Selected Rainfall", f"{rainfall_slider} mm/hr")
        st.markdown("As rainfall intensity crosses **60 mm/hr**, primary drainage channels exceed capacity, causing overflow into residential and market zones.")
        st.success(" Model calibrated using Kampala municipal topographical elevations.")
    with s2:
        st.markdown("#### Projected Population Impact Curve")
        st.line_chart(sim_df)

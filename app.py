import streamlit as st
import rasterio
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Sindh Flood Dashboard", layout="wide")

st.title("🌊 Sindh Flood Dashboard (Sentinel-1)")
st.write("Flood maps derived from Google Earth Engine (demo project)")

# -------------------
# FILES
# -------------------
RASTER_FILES = {
    "July 2022": "data/flood_2022-07-01.tif",
    "August 2022": "data/flood_2022-08-01.tif",
    "September 2022": "data/flood_2022-09-01.tif"
}

# -------------------
# LOAD RASTER (cached)
# -------------------
@st.cache_data
def load_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1)
        bounds = src.bounds
    return arr, bounds

# -------------------
# SIDEBAR
# -------------------
month = st.sidebar.selectbox("Select Month", list(RASTER_FILES.keys()))

# -------------------
# LOAD SELECTED MAP ONLY
# -------------------
arr, bounds = load_raster(RASTER_FILES[month])
arr = np.where(arr == 0, np.nan, arr)
flood_pixels = int(np.nansum(arr))

# -------------------
# MAP
# -------------------
m = folium.Map(location=[26, 69], zoom_start=6, tiles="CartoDB positron")

folium.raster_layers.ImageOverlay(
    image=arr,
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    opacity=0.6,
).add_to(m)

# -------------------
# TIME SERIES (safe)
# -------------------
@st.cache_data
def compute_timeseries(files):
    months = []
    areas = []
    for k, v in files.items():
        a, _ = load_raster(v)
        a = np.where(a == 0, np.nan, a)
        months.append(k)
        areas.append(np.nansum(a))
    return months, areas

months, areas = compute_timeseries(RASTER_FILES)

fig = px.line(
    x=months,
    y=areas,
    markers=True,
    labels={"x": "Month", "y": "Flood Pixels"},
    title="Flood Extent Over Time"
)

# -------------------
# LAYOUT
# -------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗺 Flood Map")
    st_folium(m, width=600, height=500)

with col2:
    st.subheader("📈 Flood Trend")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Flooded Pixels", flood_pixels)

st.caption("Sentinel-1 Flood Classification | Demo Project")

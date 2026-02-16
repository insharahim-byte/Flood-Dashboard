import streamlit as st
import rasterio
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Sindh Flood Dashboard", layout="wide")

st.title("🌊 Sindh Flood Dashboard (Sentinel-1)")
st.write("Interactive dashboard using flood maps exported from Google Earth Engine")

# =========================
# DATA FILES
# =========================
RASTER_FILES = {
    "July 2022": "data/flood_2022-07-01.tif",
    "August 2022": "data/flood_2022-08-01.tif",
    "September 2022": "data/flood_2022-09-01.tif"
}

# =========================
# FUNCTIONS
# =========================
@st.cache_data
def load_raster(path):
    with rasterio.open(path) as src:
        array = src.read(1)
        bounds = src.bounds
    return array, bounds

def compute_flood_pixels(array):
    masked = np.where(array == 0, np.nan, array)
    return masked, np.nansum(masked)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("🗓 Select Month")
selected_month = st.sidebar.selectbox("Flood Map", list(RASTER_FILES.keys()))

# =========================
# CHECK FILE EXISTS
# =========================
raster_path = RASTER_FILES[selected_month]

if not os.path.exists(raster_path):
    st.error(f"❌ File not found: {raster_path}")
    st.stop()

# =========================
# LOAD DATA
# =========================
raster, bounds = load_raster(raster_path)
raster, flood_pixels = compute_flood_pixels(raster)

# =========================
# MAP
# =========================
map_center = [25.5, 69]
m = folium.Map(location=map_center, zoom_start=6, tiles="CartoDB positron")

folium.raster_layers.ImageOverlay(
    image=raster,
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    opacity=0.6,
).add_to(m)

folium.LayerControl().add_to(m)

# =========================
# TIME SERIES
# =========================
months = []
areas = []

for month, path in RASTER_FILES.items():
    if os.path.exists(path):
        arr, _ = load_raster(path)
        arr, area = compute_flood_pixels(arr)
        months.append(month)
        areas.append(area)

df = pd.DataFrame({
    "Month": months,
    "Flood Pixels": areas
})

fig = px.line(
    df,
    x="Month",
    y="Flood Pixels",
    markers=True,
    title="Flood Extent Over Time"
)

# =========================
# LAYOUT
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗺 Flood Map")
    st_folium(m, width=600, height=500)

with col2:
    st.subheader("📈 Flood Trend")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Flooded Pixels", int(flood_pixels))

st.caption("Data: Sentinel-1 Flood Classification | Project Demo")

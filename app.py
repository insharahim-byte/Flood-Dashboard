import streamlit as st
import rasterio
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px

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
    "July 2022": "data/flood_2022_07.tif",
    "August 2022": "data/flood_2022_08.tif",
    "September 2022": "data/flood_2022_09.tif"
}

# =========================
# FUNCTIONS
# =========================
@st.cache_data
def load_raster(path):
    """Load raster and return array + bounds."""
    with rasterio.open(path) as src:
        array = src.read(1)
        bounds = src.bounds
    return array, bounds


def compute_flood_pixels(array):
    """Mask zeros and count flooded pixels."""
    masked = np.where(array == 0, np.nan, array)
    return masked, np.nansum(masked)


# =========================
# SIDEBAR
# =========================
st.sidebar.header("🗓 Select Month")
selected_month = st.sidebar.selectbox("Flood Map", list(RASTER_FILES.keys()))

# =========================
# LOAD SELECTED DATA
# =========================
raster, bounds = load_raster(RASTER_FILES[selected_month])
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
    colormap=lambda x: (0, 0, 1, x),
).add_to(m)

folium.LayerControl().add_to(m)

# =========================
# TIME SERIES
# =========================
months = []
areas = []

for month, path in RASTER_FILES.items():
    arr, _ = load_raster(path)
    arr, area = compute_flood_pixels(arr)
    months.append(month)
    areas.append(area)

df = {
    "Month": months,
    "Flood Pixels": areas
}

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

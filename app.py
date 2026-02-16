import streamlit as st
import rasterio
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="Sindh Flood Dashboard", layout="wide")

st.title("🌊 Sindh Flood Dashboard (Sentinel-1)")
st.write("Small project dashboard using flood maps exported from Google Earth Engine")

RASTER_FILES = {
    "July 2022": "data/flood_2022-07-01.tif",
    "August 2022": "data/flood_2022-08-01.tif",
    "September 2022": "data/flood_2022-09-01.tif"
}

@st.cache_data
def load_raster(path):
    with rasterio.open(path) as src:
        # 🔽 READ AT LOWER RESOLUTION (important)
        arr = src.read(
            1,
            out_shape=(1, src.height // 4, src.width // 4)
        )
        bounds = src.bounds
    return arr, bounds

st.sidebar.header("🗓 Select Month")
month = st.sidebar.selectbox("Flood Map:", list(RASTER_FILES.keys()))

try:
    arr, bounds = load_raster(RASTER_FILES[month])
except Exception as e:
    st.error(f"Failed to load raster: {e}")
    st.stop()

arr = np.where(arr == 0, np.nan, arr)
flood_pixels = np.nansum(arr)

m = folium.Map(location=[25.5, 69], zoom_start=6, tiles="CartoDB positron")

folium.raster_layers.ImageOverlay(
    image=arr,
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    opacity=0.6,
).add_to(m)

months = []
areas = []

for k, v in RASTER_FILES.items():
    try:
        a, _ = load_raster(v)
        a = np.where(a == 0, np.nan, a)
        months.append(k)
        areas.append(np.nansum(a))
    except:
        pass

fig = px.line(
    x=months,
    y=areas,
    markers=True,
    labels={"x": "Month", "y": "Flood Pixels"},
    title="Flood Extent Over Time"
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🗺 Flood Map")
    st_folium(m, width=600, height=500)

with col2:
    st.subheader("📈 Flood Trend")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Flooded Pixels", int(flood_pixels))

st.caption("Data: Sentinel-1 Flood Classification | Project Demo")

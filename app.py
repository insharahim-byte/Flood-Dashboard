import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys
import rasterio
import folium
from streamlit_folium import st_folium
from branca.colormap import LinearColormap

st.set_page_config(page_title="Sindh Flood Dashboard", layout="wide")

st.title("🌊 Sindh Flood Dashboard")
st.write("Flood visualization using Sentinel-1 satellite data")

DATA_FOLDER = "data"
month_to_file = {
    "July 2022": "flood_2022-07-01.tif",
    "August 2022": "flood_2022-08-01.tif",
    "September 2022": "flood_2022-09-01.tif"
}

st.sidebar.header("Controls")
selected_month = st.sidebar.selectbox(
    "Select Month",
    list(month_to_file.keys())
)

st.sidebar.subheader("Available Data")
if os.path.exists(DATA_FOLDER):
    files = os.listdir(DATA_FOLDER)
    tif_files = [f for f in files if f.endswith('.tif')]
    for file in tif_files:
        file_size = os.path.getsize(os.path.join(DATA_FOLDER, file)) / 1024
        st.sidebar.write(f"✓ {file} ({file_size:.1f} KB)")
else:
    st.sidebar.error("Data folder not found")

@st.cache_data
def load_raster(month):
    filename = month_to_file[month]
    filepath = os.path.join(DATA_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return None, None
    
    try:
        with rasterio.open(filepath) as src:
            band = src.read(1)
            bounds = src.bounds
        return band, bounds
    except Exception as e:
        st.error(f"Error loading raster: {e}")
        return None, None

raster_data, bounds = load_raster(selected_month)

sample_data = {
    "July 2022": {"extent": 1250, "depth": 1.2},
    "August 2022": {"extent": 2250, "depth": 2.1},
    "September 2022": {"extent": 1650, "depth": 1.5}
}

if raster_data is not None:
    flooded_pixels = np.sum(raster_data > 0)
    total_pixels = raster_data.size
    flood_percentage = (flooded_pixels / total_pixels) * 100
    mean_depth = np.mean(raster_data[raster_data > 0]) if flooded_pixels > 0 else 0
    max_depth = np.max(raster_data)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Flooded Pixels", f"{flooded_pixels:,}")
    with col2:
        st.metric("Area Flooded", f"{flood_percentage:.1f}%")
    with col3:
        st.metric("Mean Depth", f"{mean_depth:.2f} m")
    with col4:
        st.metric("Max Depth", f"{max_depth:.2f} m")
    
    st.subheader("Flood Extent Map")
    
    if bounds:
        center_lat = (bounds.top + bounds.bottom) / 2
        center_lon = (bounds.left + bounds.right) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")
        
        colormap = LinearColormap(
            colors=['lightblue', 'darkblue'],
            vmin=0,
            vmax=max_depth if max_depth > 0 else 1
        )
        
        from folium.raster_layers import ImageOverlay
        
        display_raster = raster_data / max_depth if max_depth > 0 else raster_data
        
        ImageOverlay(
            image=display_raster,
            bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
            opacity=0.7,
            colormap=lambda x: colormap(x * max_depth) if max_depth > 0 else (0, 0, 1, 0)
        ).add_to(m)
        
        colormap.add_to(m)
        st_folium(m, width=800, height=500)
else:
    st.info("Using sample data for visualization")
    current_data = sample_data[selected_month]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Flood Extent (km²)", current_data["extent"])
    with col2:
        st.metric("Average Depth (m)", current_data["depth"])
    
    st.subheader("Sample Flood Map")
    center_lat, center_lon = 25.5, 69.0
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="CartoDB positron")
    
    folium.Circle(
        location=[center_lat, center_lon],
        radius=50000,
        color='blue',
        fill=True,
        fillOpacity=0.3,
        popup=f"Sample flood area - {selected_month}"
    ).add_to(m)
    
    st_folium(m, width=800, height=500)

months_data = []
for month in month_to_file.keys():
    raster, _ = load_raster(month)
    if raster is not None:
        flooded = np.sum(raster > 0)
        months_data.append({
            "Month": month,
            "Flood Extent (pixels)": flooded
        })
    else:
        months_data.append({
            "Month": month,
            "Flood Extent (pixels)": sample_data[month]["extent"]
        })

df = pd.DataFrame(months_data)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig = px.bar(
        df, 
        x="Month", 
        y="Flood Extent (pixels)", 
        title="Flood Extent Over Time",
        color="Flood Extent (pixels)",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, width='stretch')

with col_chart2:
    st.subheader("Monthly Statistics")
    st.dataframe(df, width='stretch', hide_index=True)

with st.expander("System Information"):
    st.write(f"Working Directory: {os.getcwd()}")
    st.write(f"Data Folder Exists: {os.path.exists(DATA_FOLDER)}")
    if os.path.exists(DATA_FOLDER):
        st.write(f"Files: {os.listdir(DATA_FOLDER)}")
    if raster_data is not None:
        st.write(f"Raster Shape: {raster_data.shape}")
        st.write(f"Raster Range: {raster_data.min():.2f} - {raster_data.max():.2f}")
    st.write(f"Python Version: {sys.version}")

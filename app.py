import streamlit as st
import rasterio
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import os

st.set_page_config(page_title="Flood Map", layout="wide")

st.title("Flood Extent & Depth")
st.write("Based on Sentinel-1 data")

# ONLY ONE FILE - HARDCODED
TIF_FILE = "data/flood_2022-08-01.tif"  # Change this to whichever file you want

# Check if file exists
if not os.path.exists(TIF_FILE):
    st.error(f"File not found: {TIF_FILE}")
    st.stop()

# Load the raster
try:
    with rasterio.open(TIF_FILE) as src:
        raster = src.read(1)
        bounds = src.bounds
        transform = src.transform
    st.success("✅ File loaded successfully!")
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# Calculate ONLY depth and extent
flooded_area = np.sum(raster > 0)  # Extent (pixels)
max_depth = np.max(raster)          # Max depth
avg_depth = np.mean(raster[raster > 0]) if flooded_area > 0 else 0  # Avg depth

# Display ONLY what you want
col1, col2 = st.columns(2)

with col1:
    st.metric("Flood Extent", f"{flooded_area:,} pixels")

with col2:
    st.metric("Max Depth", f"{max_depth:.2f} m")
    st.metric("Avg Depth", f"{avg_depth:.2f} m")

# Create map
st.subheader("Flood Map")

# Center map on the raster
center_lat = (bounds.top + bounds.bottom) / 2
center_lon = (bounds.left + bounds.right) / 2

m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# Add flood overlay
from folium.raster_layers import ImageOverlay

# Normalize for display
if max_depth > 0:
    display_raster = raster / max_depth
else:
    display_raster = raster

ImageOverlay(
    image=display_raster,
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    opacity=0.7,
    colormap=lambda x: [0, 0, x, 0.8]  # Blue scale
).add_to(m)

st_folium(m, width=800, height=500)

# Show file info
with st.expander("File Info"):
    st.write(f"File: {TIF_FILE}")
    st.write(f"Size: {os.path.getsize(TIF_FILE) / (1024*1024):.1f} MB")
    st.write(f"Shape: {raster.shape}")
    st.write(f"Depth range: {raster.min():.2f} - {raster.max():.2f}")

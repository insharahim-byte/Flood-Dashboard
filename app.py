import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Sindh Flood Dashboard", layout="wide")

st.title("🌊 Sindh Flood Dashboard")
st.write("Interactive flood visualization dashboard")

# Simple sidebar
st.sidebar.header("Controls")
selected_month = st.sidebar.selectbox(
    "Select Month",
    ["July 2022", "August 2022", "September 2022"]
)

# Check what files exist
DATA_FOLDER = "data"
st.sidebar.subheader("📁 Data Files")
if os.path.exists(DATA_FOLDER):
    files = os.listdir(DATA_FOLDER)
    for file in files:
        file_size = os.path.getsize(os.path.join(DATA_FOLDER, file)) / 1024  # KB
        st.sidebar.write(f"✅ {file} ({file_size:.1f} KB)")
else:
    st.sidebar.error("Data folder not found!")

# Sample flood data (since raster reading might be complex)
flood_data = {
    "July 2022": {"extent": 1250, "depth": 1.2, "cities": 3},
    "August 2022": {"extent": 2250, "depth": 2.1, "cities": 5},
    "September 2022": {"extent": 1650, "depth": 1.5, "cities": 4}
}

# Get current month's data
current_data = flood_data[selected_month]

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Flood Extent (km²)", current_data["extent"])
with col2:
    st.metric("Average Depth (m)", current_data["depth"])
with col3:
    st.metric("Cities Affected", current_data["cities"])

# Create trend chart
df = pd.DataFrame({
    "Month": list(flood_data.keys()),
    "Flood Extent (km²)": [flood_data[m]["extent"] for m in flood_data.keys()],
    "Average Depth (m)": [flood_data[m]["depth"] for m in flood_data.keys()]
})

# Two columns for charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig1 = px.bar(df, x="Month", y="Flood Extent (km²)", 
                  title="Flood Extent Over Time",
                  color="Flood Extent (km²)",
                  color_continuous_scale="Blues")
    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    fig2 = px.line(df, x="Month", y="Average Depth (m)", 
                   title="Flood Depth Trend",
                   markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# Map placeholder (simplified)
st.subheader("🗺 Flood Map")
st.info("📍 Map visualization would appear here with actual raster data")
col_map1, col_map2, col_map3 = st.columns(3)
with col_map1:
    st.metric("North Region", f"{current_data['extent']*0.4:.0f} km²")
with col_map2:
    st.metric("Central Region", f"{current_data['extent']*0.35:.0f} km²")
with col_map3:
    st.metric("South Region", f"{current_data['extent']*0.25:.0f} km²")

# Data table
st.subheader("📊 Detailed Data")
st.dataframe(df, use_container_width=True)

# Success message
st.success("✅ Dashboard loaded successfully!")

# Debug section
with st.expander("🔧 Debug Info"):
    st.write("Current working directory:", os.getcwd())
    st.write("Data folder exists:", os.path.exists(DATA_FOLDER))
    if os.path.exists(DATA_FOLDER):
        st.write("Files in data folder:", os.listdir(DATA_FOLDER))
    st.write("Python version:", import sys; sys.version)

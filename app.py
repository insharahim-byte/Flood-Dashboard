import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Flood Map", layout="wide")

st.title("🌊 Sindh Flood Depth")
st.write("Gradient flood map")

# ================== YOUR DATA ==================
districts = {
    "Karachi": {"lat": 24.86, "lon": 67.01, "depth": 2.5},
    "Hyderabad": {"lat": 25.38, "lon": 68.37, "depth": 1.8},
    "Sukkur": {"lat": 27.70, "lon": 68.87, "depth": 3.2},
    "Larkana": {"lat": 27.56, "lon": 68.21, "depth": 1.2},
    "Dadu": {"lat": 26.73, "lon": 67.78, "depth": 4.0},
    "Jacobabad": {"lat": 28.28, "lon": 68.44, "depth": 0.8},
    "Shikarpur": {"lat": 27.96, "lon": 68.65, "depth": 1.5},
    "Khairpur": {"lat": 27.53, "lon": 68.76, "depth": 1.1},
    "Nawabshah": {"lat": 26.24, "lon": 68.41, "depth": 2.8},
    "Mirpurkhas": {"lat": 25.53, "lon": 69.02, "depth": 1.6},
    "Umerkot": {"lat": 25.36, "lon": 69.74, "depth": 0.9},
    "Tharparkar": {"lat": 24.89, "lon": 70.20, "depth": 0.5},
    "Badin": {"lat": 24.66, "lon": 68.84, "depth": 3.5},
    "Thatta": {"lat": 24.75, "lon": 67.92, "depth": 2.2},
    "Jamshoro": {"lat": 25.43, "lon": 68.28, "depth": 1.4},
}

df = pd.DataFrame.from_dict(districts, orient='index')
df.reset_index(inplace=True)
df.rename(columns={'index': 'District'}, inplace=True)

# ================== CREATE GRADIENT ==================
# Simple grid
lat = np.linspace(24, 29, 100)
lon = np.linspace(66, 71, 100)
LON, LAT = np.meshgrid(lon, lat)

# Create depth grid
DEPTH = np.zeros_like(LAT)

for _, row in df.iterrows():
    dist = np.sqrt(((LAT - row['lat'])/0.5)**2 + ((LON - row['lon'])/0.7)**2)
    influence = np.exp(-dist) * row['depth']
    DEPTH += influence

DEPTH = DEPTH / DEPTH.max() * df['depth'].max()

# ================== SIDEBAR ==================
color_scheme = st.sidebar.selectbox(
    "Color Scheme",
    ["RdBu", "Viridis", "Plasma", "Hot", "Blues", "YlOrRd"]
)

# ================== SIMPLE METRICS ==================
st.metric("Maximum Flood Depth", f"{df['depth'].max():.1f} meters")

# ================== SIMPLE MAP (NO COLORBAR ISSUES) ==================
st.subheader("Flood Depth Map")

# SUPER SIMPLE - just the heatmap with minimal parameters
fig = go.Figure()

fig.add_trace(go.Heatmap(
    z=DEPTH,
    x=lon,
    y=lat,
    colorscale=color_scheme,
    colorbar=dict(title="Depth (m)")  # Simple colorbar
))

fig.update_layout(
    xaxis_title="Longitude",
    yaxis_title="Latitude",
    height=600,
    width=800
)

st.plotly_chart(fig)

# ================== SIMPLE BAR CHART ==================
st.subheader("Depth by District")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df['District'],
    y=df['depth'],
    marker_color=df['depth'],
    marker_colorscale=color_scheme
))

fig2.update_layout(
    xaxis_tickangle=-45,
    yaxis_title="Depth (m)",
    height=400
)

st.plotly_chart(fig2)

# ================== SIMPLE TABLE ==================
st.subheader("District Data")
st.dataframe(df[['District', 'depth']].sort_values('depth', ascending=False))

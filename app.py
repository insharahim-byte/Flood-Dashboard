import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(page_title="Sindh Flood Depth Dashboard", layout="wide")

# Title and description
st.title("🌊 Sindh Flood Depth Dashboard (2022 Inspired)")
st.markdown("Gradient-based flood depth/intensity map across Sindh districts. Darker red = higher estimated flood depth/impact.")

# ================== DATA ==================
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

df = pd.DataFrame.from_dict(districts, orient='index').reset_index()
df.rename(columns={'index': 'District'}, inplace=True)

# ================== GRID & GRADIENT CREATION ==================
# Grid covering Sindh roughly (lat 24–29, lon 66–71)
lat = np.linspace(24.0, 29.0, 150)   # Higher resolution for smoother gradient
lon = np.linspace(66.0, 71.0, 150)
LON, LAT = np.meshgrid(lon, lat)

DEPTH = np.zeros_like(LAT, dtype=float)

for _, row in df.iterrows():
    # Distance with aspect ratio adjustment (lon/lat not square at this latitude)
    dist = np.sqrt( ((LAT - row['lat']) / 0.45)**2 + ((LON - row['lon']) / 0.70)**2 )
    # Gaussian-like influence (strong near point, decays quickly)
    influence = row['depth'] * np.exp(-dist**2 / (2 * 0.8**2))   # tighter decay
    DEPTH += influence

# Normalize to max observed depth
if DEPTH.max() > 0:
    DEPTH = DEPTH / DEPTH.max() * df['depth'].max()

# ================== SIDEBAR ==================
st.sidebar.header("Visualization Options")
color_scheme = st.sidebar.selectbox(
    "Color Scale (like severity map)",
    ["YlOrRd", "Reds", "OrRd", "Hot", "YlOrBr", "RdPu", "Plasma"]
)
opacity = st.sidebar.slider("Heatmap Opacity", 0.3, 1.0, 0.75, step=0.05)

# ================== METRICS ==================
col1, col2, col3 = st.columns(3)
col1.metric("Max Flood Depth", f"{df['depth'].max():.1f} m")
col2.metric("Most Affected District", df.loc[df['depth'].idxmax(), 'District'])
col3.metric("Number of Districts", len(df))

# ================== MAIN MAP ==================
st.subheader("Sindh Flood Depth / Intensity Gradient")

fig = go.Figure()

# Heatmap layer (main gradient)
fig.add_trace(go.Heatmap(
    z=DEPTH,
    x=lon,
    y=lat,
    colorscale=color_scheme,
    opacity=opacity,
    colorbar=dict(
        title="Depth (m)",
        titleside="right",
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4],
        ticktext=["Low", "1", "2", "3", "Severe"],
    ),
    showscale=True,
    zmin=0,
    zmax=df['depth'].max(),
))

# Overlay district points with labels (like dots on the map)
fig.add_trace(go.Scattergeo(
    lon=df['lon'],
    lat=df['lat'],
    text=df['District'] + ": " + df['depth'].astype(str) + " m",
    mode='markers+text',
    marker=dict(
        size=12,
        color=df['depth'],
        colorscale=color_scheme,
        cmin=0,
        cmax=df['depth'].max(),
        line=dict(width=1, color='black')
    ),
    textposition="top center",
    hoverinfo="text",
))

fig.update_layout(
    title="Estimated Flood Depth Gradient - Sindh (2022 Reference)",
    geo=dict(
        scope='asia',
        center=dict(lat=26.0, lon=68.5),
        lonaxis_range=[66, 71],
        lataxis_range=[24, 29],
        projection_type='natural earth',
        showcountries=True,
        countrycolor="gray",
        showsubunits=True,
        subunitcolor="lightgray",
        bgcolor="rgba(0,0,0,0)",
    ),
    height=700,
    margin={"r":0,"t":50,"l":0,"b":0},
)

st.plotly_chart(fig, use_container_width=True)

# ================== BAR CHART ==================
st.subheader("Flood Depth by District (Sorted)")
fig_bar = px.bar(
    df.sort_values('depth', ascending=False),
    x='District',
    y='depth',
    color='depth',
    color_continuous_scale=color_scheme,
    labels={'depth': 'Depth (m)'},
    height=450
)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# ================== TABLE ==================
st.subheader("District Data Table")
st.dataframe(
    df[['District', 'depth']].sort_values('depth', ascending=False)
    .style.format({'depth': '{:.1f} m'})
    .background_gradient(cmap='YlOrRd', subset=['depth'])
)

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Flood Analysis", layout="wide")

st.title("🌊 Sindh Flood Depth Map")
st.write("Continuous flood gradient visualization")

# ================== YOUR DISTRICT DATA ==================
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

# Convert to DataFrame
df = pd.DataFrame.from_dict(districts, orient='index')
df.reset_index(inplace=True)
df.rename(columns={'index': 'District'}, inplace=True)

# ================== CREATE GRADIENT ==================
# Create grid
lat = np.linspace(24, 29, 150)
lon = np.linspace(66, 71, 150)
LON, LAT = np.meshgrid(lon, lat)

# Initialize depth grid
DEPTH = np.zeros_like(LAT)

# Add influence from each district
for _, row in df.iterrows():
    # Calculate distance-based influence
    dist = np.sqrt(((LAT - row['lat'])/0.5)**2 + ((LON - row['lon'])/0.7)**2)
    influence = np.exp(-dist) * row['depth']
    DEPTH += influence

# Normalize
DEPTH = DEPTH / DEPTH.max() * df['depth'].max()

# ================== SIDEBAR ==================
st.sidebar.header("Settings")
colors = st.sidebar.selectbox(
    "Color Scheme",
    ["RdBu", "Viridis", "Plasma", "Hot", "Jet", "Blues", "YlOrRd"]
)
opacity = st.sidebar.slider("Opacity", 0.5, 1.0, 0.8)

# ================== METRICS ==================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Max Depth", f"{df['depth'].max():.1f} m")
with col2:
    st.metric("Avg Depth", f"{df['depth'].mean():.1f} m")
with col3:
    st.metric("Districts", len(df))

# ================== GRADIENT MAP (FIXED) ==================
st.subheader("🗺 Flood Depth Gradient")

fig = go.Figure()

# Add heatmap (fixed version - removed problematic colorbar parameter)
fig.add_trace(go.Heatmap(
    z=DEPTH,
    x=lon,
    y=lat,
    colorscale=colors,
    opacity=opacity,
    hoverongaps=False,
    hovertemplate='Lat: %{y:.2f}<br>Lon: %{x:.2f}<br>Depth: %{z:.1f} m<extra></extra>',
    colorbar=dict(
        title="Depth (m)",
        titleside="right",
        thickness=20
    )
))

# Update layout for map-like appearance
fig.update_layout(
    xaxis=dict(
        title="Longitude",
        range=[66, 71],
        constrain='domain'
    ),
    yaxis=dict(
        title="Latitude",
        range=[24, 29],
        scaleanchor="x",
        scaleratio=1
    ),
    height=600,
    margin=dict(l=50, r=50, t=30, b=50),
    plot_bgcolor='lightgray'
)

# Add background map effect
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='white')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='white')

st.plotly_chart(fig, use_container_width=True)

# ================== DEPTH CHART ==================
st.subheader("📊 Depth by District")

# Sort by depth
df_sorted = df.sort_values('depth', ascending=True)

fig_bars = go.Figure()
fig_bars.add_trace(go.Bar(
    y=df_sorted['District'],
    x=df_sorted['depth'],
    orientation='h',
    marker=dict(
        color=df_sorted['depth'],
        colorscale=colors,
        showscale=True,
        colorbar=dict(title="Depth (m)")
    ),
    text=df_sorted['depth'].round(1),
    textposition='outside'
))

fig_bars.update_layout(
    xaxis_title="Depth (m)",
    height=500,
    margin=dict(l=100, r=50, t=30, b=50)
)

st.plotly_chart(fig_bars, use_container_width=True)

# ================== DATA TABLE ==================
st.subheader("📋 District Details")
st.dataframe(
    df[['District', 'depth']].sort_values('depth', ascending=False),
    column_config={
        "District": "District",
        "depth": st.column_config.NumberColumn("Depth (m)", format="%.1f")
    },
    use_container_width=True,
    hide_index=True
)

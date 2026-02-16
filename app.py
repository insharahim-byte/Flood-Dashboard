import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Flood Analysis", layout="wide")

st.title("🌊 Flood Extent & Depth")
st.write("Continuous flood gradient map")

# ================== YOUR DISTRICT DATA ==================
# This data creates the gradient pattern
districts = {
    "Karachi": {"lat": 24.86, "lon": 67.01, "extent": 450, "depth": 2.5},
    "Hyderabad": {"lat": 25.38, "lon": 68.37, "extent": 380, "depth": 1.8},
    "Sukkur": {"lat": 27.70, "lon": 68.87, "extent": 520, "depth": 3.2},
    "Larkana": {"lat": 27.56, "lon": 68.21, "extent": 290, "depth": 1.2},
    "Dadu": {"lat": 26.73, "lon": 67.78, "extent": 610, "depth": 4.0},
    "Jacobabad": {"lat": 28.28, "lon": 68.44, "extent": 180, "depth": 0.8},
    "Shikarpur": {"lat": 27.96, "lon": 68.65, "extent": 320, "depth": 1.5},
    "Khairpur": {"lat": 27.53, "lon": 68.76, "extent": 275, "depth": 1.1},
    "Nawabshah": {"lat": 26.24, "lon": 68.41, "extent": 490, "depth": 2.8},
    "Mirpurkhas": {"lat": 25.53, "lon": 69.02, "extent": 340, "depth": 1.6},
    "Umerkot": {"lat": 25.36, "lon": 69.74, "extent": 210, "depth": 0.9},
    "Tharparkar": {"lat": 24.89, "lon": 70.20, "extent": 150, "depth": 0.5},
    "Badin": {"lat": 24.66, "lon": 68.84, "extent": 580, "depth": 3.5},
    "Thatta": {"lat": 24.75, "lon": 67.92, "extent": 420, "depth": 2.2},
    "Jamshoro": {"lat": 25.43, "lon": 68.28, "extent": 310, "depth": 1.4},
}

# Convert to DataFrame
df = pd.DataFrame.from_dict(districts, orient='index')
df.reset_index(inplace=True)
df.rename(columns={'index': 'District'}, inplace=True)

# ================== CREATE GRADIENT GRID ==================
# Create a fine grid for smooth gradient
lat_grid = np.linspace(24, 29, 200)
lon_grid = np.linspace(66, 71, 200)
lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

# Initialize depth grid
depth_grid = np.zeros_like(lat_mesh)

# For each district, add a Gaussian influence to create smooth gradient
for _, row in df.iterrows():
    # Gaussian influence: exp(-distance^2 / spread^2)
    distance = np.sqrt(((lat_mesh - row['lat'])**2 / 0.3) + ((lon_mesh - row['lon'])**2 / 0.4))
    influence = np.exp(-distance) * row['depth']
    depth_grid += influence

# Normalize
depth_grid = depth_grid / depth_grid.max() * df['depth'].max()

# ================== SIDEBAR ==================
st.sidebar.header("Visualization Settings")
opacity = st.sidebar.slider("Map Opacity", 0.3, 1.0, 0.8)
color_scale = st.sidebar.selectbox(
    "Color Scheme",
    ["Viridis", "Plasma", "Inferno", "Magma", "RdBu", "Jet", "Hot"]
)

# ================== MAIN METRICS ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Area", "~25,000 km²")
with col2:
    st.metric("Max Depth", f"{df['depth'].max():.1f} m")
with col3:
    st.metric("Avg Depth", f"{df['depth'].mean():.1f} m")

# ================== GRADIENT MAP ==================
st.subheader("🗺 Flood Depth Gradient Map")

fig = go.Figure()

# Add the gradient heatmap - THIS IS THE KEY PART
fig.add_trace(go.Contour(
    z=depth_grid,
    x=lon_grid,
    y=lat_grid,
    colorscale=color_scale,
    opacity=opacity,
    contours=dict(
        coloring='heatmap',
        showlabels=True,
        labelfont=dict(size=12, color='white')
    ),
    colorbar=dict(
        title="Depth (m)",
        titleside="right",
        thickness=20,
        len=0.8
    ),
    hovertemplate='Lat: %{y:.2f}<br>Lon: %{x:.2f}<br>Depth: %{z:.1f} m<extra></extra>'
))

# Add district boundaries (optional - remove if you want just gradient)
# You can comment this out if you want NO lines at all
fig.add_trace(go.Scattergeo(
    lon=df['lon'],
    lat=df['lat'],
    mode='text',
    text=df['District'],
    textfont=dict(size=9, color='white', family='Arial'),
    showlegend=False,
    hoverinfo='none'
))

# Update map layout
fig.update_layout(
    geo=dict(
        scope='asia',
        showland=True,
        landcolor='rgb(240, 240, 240)',
        coastlinecolor='rgb(100, 100, 100)',
        showocean=True,
        oceancolor='rgb(230, 240, 255)',
        showlakes=True,
        lakecolor='rgb(200, 220, 250)',
        showrivers=True,
        rivercolor='rgb(150, 180, 230)',
        center=dict(lat=26.5, lon=68.5),
        projection_scale=7,
        lonaxis_range=[66, 71],
        lataxis_range=[24, 29]
    ),
    height=600,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ================== DEPTH DISTRIBUTION ==================
st.subheader("📊 Depth Distribution")

col_hist, col_stats = st.columns([2, 1])

with col_hist:
    # Create histogram of depths
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df['depth'],
        nbinsx=15,
        marker_color='#1f77b4',
        opacity=0.8
    ))
    fig_hist.update_layout(
        xaxis_title="Depth (m)",
        yaxis_title="Number of Districts",
        height=300,
        margin=dict(l=40, r=40, t=30, b=40)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_stats:
    # Summary statistics
    st.dataframe(
        df['depth'].describe().round(2).to_frame(),
        column_config={"depth": "Statistics"},
        use_container_width=True
    )

# ================== DISTRICT TABLE ==================
st.subheader("📋 District Details")
st.dataframe(
    df[['District', 'extent', 'depth']].sort_values('depth', ascending=False),
    column_config={
        "District": "District",
        "extent": st.column_config.NumberColumn("Extent (km²)", format="%.0f"),
        "depth": st.column_config.NumberColumn("Depth (m)", format="%.1f")
    },
    use_container_width=True,
    hide_index=True
)

# ================== COLOR LEGEND ==================
with st.expander("ℹ️ About this map"):
    st.markdown(f"""
    - **Smooth gradient** created from {len(df)} district data points
    - **Colors**: {color_scale} scheme (darker = deeper water)
    - **Resolution**: 200x200 grid for smooth appearance
    - Hover anywhere to see estimated flood depth
    """)

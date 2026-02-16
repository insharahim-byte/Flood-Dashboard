import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Flood Analysis", layout="wide")

st.title("🌊 Sindh Flood Extent & Depth")
st.write("Interactive flood visualization")

# ================== YOUR DATA GOES HERE ==================
# REPLACE THIS WITH YOUR ACTUAL DISTRICT DATA
locations = {
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
# ================== END OF YOUR DATA ==================

# Convert to DataFrame
df = pd.DataFrame.from_dict(locations, orient='index')
df.reset_index(inplace=True)
df.rename(columns={'index': 'District'}, inplace=True)

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("Filters")
min_extent = st.sidebar.slider("Min Flood Extent (km²)", 0, 700, 0)
min_depth = st.sidebar.slider("Min Flood Depth (m)", 0.0, 5.0, 0.0)

# Filter data
filtered_df = df[(df['extent'] >= min_extent) & (df['depth'] >= min_depth)]

st.sidebar.write(f"Showing {len(filtered_df)} of {len(df)} districts")

# ================== MAIN METRICS ==================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Districts", len(df))
with col2:
    st.metric("Affected Districts", len(filtered_df))
with col3:
    st.metric("Total Flood Extent", f"{filtered_df['extent'].sum():,.0f} km²")
with col4:
    st.metric("Max Depth", f"{filtered_df['depth'].max():.1f} m")

# ================== MAP ==================
st.subheader("🗺 Flood Map")

fig_map = go.Figure()

fig_map.add_trace(go.Scattergeo(
    lon=filtered_df['lon'],
    lat=filtered_df['lat'],
    text=filtered_df['District'],
    mode='markers+text',
    marker=dict(
        size=filtered_df['extent'] / 8,
        color=filtered_df['depth'],
        colorscale='RdYlBu_r',  # Red for deep, blue for shallow
        showscale=True,
        colorbar=dict(title="Depth (m)"),
        line=dict(width=1, color='black'),
        sizemode='area',
        sizeref=2.*max(filtered_df['extent'])/(40.**2),
    ),
    textposition="top center",
    textfont=dict(size=10, color='black'),
    hovertemplate='<b>%{text}</b><br>' +
                  'Extent: %{marker.size:.0f} km²<br>' +
                  'Depth: %{marker.color:.1f} m<br>' +
                  '<extra></extra>'
))

fig_map.update_layout(
    geo=dict(
        scope='asia',
        showland=True,
        landcolor='rgb(240, 240, 240)',
        coastlinecolor='rgb(100, 100, 100)',
        showocean=True,
        oceancolor='rgb(220, 235, 255)',
        center=dict(lat=26.5, lon=68.5),
        projection_scale=6,
        lonaxis_range=[66, 71],
        lataxis_range=[24, 29]
    ),
    height=550,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig_map, use_container_width=True)

# ================== CHARTS ==================
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Flood Extent")
    fig_extent = px.bar(
        filtered_df.sort_values('extent', ascending=True),
        x='extent',
        y='District',
        orientation='h',
        color='extent',
        color_continuous_scale='Reds',
        labels={'extent': 'Extent (km²)'}
    )
    st.plotly_chart(fig_extent, use_container_width=True)

with col_chart2:
    st.subheader("Flood Depth")
    fig_depth = px.bar(
        filtered_df.sort_values('depth', ascending=True),
        x='depth',
        y='District',
        orientation='h',
        color='depth',
        color_continuous_scale='Blues',
        labels={'depth': 'Depth (m)'}
    )
    st.plotly_chart(fig_depth, use_container_width=True)

# ================== DATA TABLE ==================
st.subheader("📊 District Details")
st.dataframe(
    filtered_df[['District', 'extent', 'depth']].sort_values('extent', ascending=False),
    column_config={
        "District": "District",
        "extent": st.column_config.NumberColumn("Flood Extent (km²)", format="%.0f"),
        "depth": st.column_config.NumberColumn("Flood Depth (m)", format="%.1f")
    },
    use_container_width=True,
    hide_index=True
)

# ================== LEGEND ==================
with st.expander("ℹ️ How to read this map"):
    st.markdown("""
    - **Circle size** = Flood extent (larger = more area flooded)
    - **Circle color** = Flood depth (red = deeper, blue = shallower)
    - Hover over any point to see exact numbers
    - Use filters in sidebar to focus on severe flooding
    """)

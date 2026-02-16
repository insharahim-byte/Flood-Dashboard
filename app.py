import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json

st.set_page_config(page_title="Sindh Flood Analysis", layout="wide")

st.title("🌊 Sindh Flood Monitoring")
st.markdown("District-wise flood extent and depth analysis")

# ================== LOAD SINDH BOUNDARY ==================
try:
    with open("sindh dist.geojson") as f:
        sindh_geo = json.load(f)
    st.sidebar.success("✅ Sindh boundary loaded")
except:
    st.sidebar.error("❌ sindh dist.geojson not found")
    sindh_geo = None

# ================== DISTRICT DATA ==================
districts_data = {
    "District": ["Karachi", "Hyderabad", "Sukkur", "Larkana", "Dadu", 
                 "Jacobabad", "Shikarpur", "Khairpur", "Nawabshah", 
                 "Mirpurkhas", "Umerkot", "Tharparkar", "Badin", "Thatta", "Jamshoro"],
    "Lat": [24.86, 25.38, 27.70, 27.56, 26.73, 28.28, 27.96, 27.53, 
            26.24, 25.53, 25.36, 24.89, 24.66, 24.75, 25.43],
    "Lon": [67.01, 68.37, 68.87, 68.21, 67.78, 68.44, 68.65, 68.76, 
            68.41, 69.02, 69.74, 70.20, 68.84, 67.92, 68.28],
    "Extent": [450, 380, 520, 290, 610, 180, 320, 275, 490, 340, 210, 150, 580, 420, 310],
    "Depth": [2.5, 1.8, 3.2, 1.2, 4.0, 0.8, 1.5, 1.1, 2.8, 1.6, 0.9, 0.5, 3.5, 2.2, 1.4]
}

df = pd.DataFrame(districts_data)

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("Filters")
show_boundary = st.sidebar.checkbox("Show Sindh Boundary", True)
min_extent = st.sidebar.slider("Minimum Extent (km²)", 0, 700, 0)
min_depth = st.sidebar.slider("Minimum Depth (m)", 0.0, 5.0, 0.0)

filtered_df = df[(df['Extent'] >= min_extent) & (df['Depth'] >= min_depth)]

# ================== METRICS ==================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Districts", len(df))
with col2:
    st.metric("Affected Districts", len(filtered_df))
with col3:
    st.metric("Total Extent", f"{filtered_df['Extent'].sum():,} km²")
with col4:
    st.metric("Max Depth", f"{filtered_df['Depth'].max():.1f} m")

# ================== MAIN MAP ==================
st.subheader("🗺️ Flood Map")

fig = go.Figure()

# Add Sindh boundary
if sindh_geo and show_boundary:
    for feature in sindh_geo['features']:
        if feature['geometry']['type'] == 'Polygon':
            coords = feature['geometry']['coordinates'][0]
            lon, lat = zip(*coords)
            fig.add_trace(go.Scattergeo(
                lon=lon,
                lat=lat,
                mode='lines',
                line=dict(color='black', width=1.5),
                name='Sindh Boundary',
                showlegend=False,
                hoverinfo='none'
            ))
        elif feature['geometry']['type'] == 'MultiPolygon':
            for polygon in feature['geometry']['coordinates']:
                coords = polygon[0]
                lon, lat = zip(*coords)
                fig.add_trace(go.Scattergeo(
                    lon=lon,
                    lat=lat,
                    mode='lines',
                    line=dict(color='black', width=1.5),
                    name='Sindh Boundary',
                    showlegend=False,
                    hoverinfo='none'
                ))

# Add flood bubbles
fig.add_trace(go.Scattergeo(
    lon=filtered_df['Lon'],
    lat=filtered_df['Lat'],
    text=filtered_df['District'],
    mode='markers+text',
    marker=dict(
        size=filtered_df['Extent'] / 6,
        color=filtered_df['Depth'],
        colorscale='Reds',
        showscale=True,
        colorbar=dict(
            title="Depth (m)",
            x=1.05,
            len=0.6,
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['0m', '1m', '2m', '3m', '4m+']
        ),
        line=dict(width=1, color='black'),
        sizemode='area',
        sizeref=2.*max(filtered_df['Extent'])/(50.**2),
        cmin=0,
        cmax=4
    ),
    textposition="top center",
    textfont=dict(size=11, color='black', family='Arial Black'),
    hoverinfo='text',
    hovertext=[
        f"<b>{d}</b><br>Extent: {e:.0f} km²<br>Depth: {dp:.1f} m"
        for d, e, dp in zip(filtered_df['District'], filtered_df['Extent'], filtered_df['Depth'])
    ]
))

fig.update_layout(
    geo=dict(
        scope='asia',
        showland=True,
        landcolor='rgb(240, 240, 240)',
        coastlinecolor='gray',
        showcountries=True,
        countrycolor='gray',
        showsubunits=True,
        subunitcolor='lightgray',
        center=dict(lat=26.5, lon=68.5),
        lonaxis_range=[66, 71],
        lataxis_range=[24, 29],
        projection_scale=6
    ),
    height=650,
    margin=dict(l=0, r=70, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=False, width=1200)

# ================== DEPTH LEGEND ==================
st.subheader("💧 Depth Categories")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.info("🟦 **0-1m** Low")
with col2:
    st.info("🟩 **1-2m** Moderate")
with col3:
    st.warning("🟨 **2-3m** High")
with col4:
    st.error("🟧 **3-4m** Severe")
with col5:
    st.error("🟥 **4m+** Extreme")

# ================== DEPTH TABLE ==================
st.subheader("📊 Depth Ranking")
depth_df = filtered_df[['District', 'Depth']].sort_values('Depth', ascending=False)
depth_df['Risk'] = depth_df['Depth'].apply(lambda x: 
    'EXTREME' if x >= 3 else 
    'SEVERE' if x >= 2 else 
    'HIGH' if x >= 1 else 
    'MODERATE')

st.dataframe(
    depth_df,
    column_config={
        "District": "District",
        "Depth": st.column_config.NumberColumn("Depth (m)", format="%.1f"),
        "Risk": "Risk Level"
    },
    hide_index=True,
    use_container_width=False,
    width=800
)

# ================== EXTENT CHART ==================
st.subheader("📊 Flood Extent")
fig_extent = px.bar(
    filtered_df.sort_values('Extent', ascending=True),
    y='District',
    x='Extent',
    orientation='h',
    color='Extent',
    color_continuous_scale='Reds',
    text='Extent'
)
fig_extent.update_traces(texttemplate='%{text:.0f} km²', textposition='outside')
fig_extent.update_layout(height=400, xaxis_title="km²", yaxis_title="")
st.plotly_chart(fig_extent, use_container_width=False, width=1000)

# ================== SUMMARY ==================
st.subheader("📋 District Summary")
summary_df = filtered_df[['District', 'Extent', 'Depth']].copy()
summary_df.columns = ['District', 'Extent (km²)', 'Depth (m)']
summary_df = summary_df.sort_values('Depth (m)', ascending=False)

st.dataframe(
    summary_df,
    column_config={
        "District": "District",
        "Extent (km²)": st.column_config.NumberColumn(format="%.0f"),
        "Depth (m)": st.column_config.NumberColumn(format="%.1f")
    },
    hide_index=True,
    use_container_width=False,
    width=800
)

# ================== DOWNLOAD ==================
csv = summary_df.to_csv(index=False)
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="sindh_flood_data.csv",
    mime="text/csv"
)

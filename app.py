import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(page_title="Sindh Flood Depth", layout="wide")

# Title
st.title("🌊 Sindh Flood Depth Map")
st.markdown("District-wise flood depth visualization")

# ================== DISTRICT DATA WITH BOUNDARIES ==================
# Each district has approximate boundary coordinates
district_boundaries = {
    "Karachi": {
        "lat": [24.7, 25.1, 25.1, 24.7, 24.7],
        "lon": [66.8, 66.8, 67.3, 67.3, 66.8],
        "depth": 2.5,
        "center": [24.86, 67.01]
    },
    "Hyderabad": {
        "lat": [25.2, 25.6, 25.6, 25.2, 25.2],
        "lon": [68.1, 68.1, 68.6, 68.6, 68.1],
        "depth": 1.8,
        "center": [25.38, 68.37]
    },
    "Sukkur": {
        "lat": [27.5, 27.9, 27.9, 27.5, 27.5],
        "lon": [68.6, 68.6, 69.1, 69.1, 68.6],
        "depth": 3.2,
        "center": [27.70, 68.87]
    },
    "Larkana": {
        "lat": [27.4, 27.8, 27.8, 27.4, 27.4],
        "lon": [68.0, 68.0, 68.5, 68.5, 68.0],
        "depth": 1.2,
        "center": [27.56, 68.21]
    },
    "Dadu": {
        "lat": [26.5, 26.9, 26.9, 26.5, 26.5],
        "lon": [67.5, 67.5, 68.0, 68.0, 67.5],
        "depth": 4.0,
        "center": [26.73, 67.78]
    },
    "Jacobabad": {
        "lat": [28.1, 28.5, 28.5, 28.1, 28.1],
        "lon": [68.2, 68.2, 68.7, 68.7, 68.2],
        "depth": 0.8,
        "center": [28.28, 68.44]
    },
    "Shikarpur": {
        "lat": [27.8, 28.2, 28.2, 27.8, 27.8],
        "lon": [68.4, 68.4, 68.9, 68.9, 68.4],
        "depth": 1.5,
        "center": [27.96, 68.65]
    },
    "Khairpur": {
        "lat": [27.3, 27.7, 27.7, 27.3, 27.3],
        "lon": [68.5, 68.5, 69.0, 69.0, 68.5],
        "depth": 1.1,
        "center": [27.53, 68.76]
    },
    "Nawabshah": {
        "lat": [26.0, 26.4, 26.4, 26.0, 26.0],
        "lon": [68.2, 68.2, 68.7, 68.7, 68.2],
        "depth": 2.8,
        "center": [26.24, 68.41]
    },
    "Mirpurkhas": {
        "lat": [25.3, 25.7, 25.7, 25.3, 25.3],
        "lon": [68.8, 68.8, 69.3, 69.3, 68.8],
        "depth": 1.6,
        "center": [25.53, 69.02]
    },
    "Umerkot": {
        "lat": [25.2, 25.6, 25.6, 25.2, 25.2],
        "lon": [69.5, 69.5, 70.0, 70.0, 69.5],
        "depth": 0.9,
        "center": [25.36, 69.74]
    },
    "Tharparkar": {
        "lat": [24.7, 25.1, 25.1, 24.7, 24.7],
        "lon": [70.0, 70.0, 70.5, 70.5, 70.0],
        "depth": 0.5,
        "center": [24.89, 70.20]
    },
    "Badin": {
        "lat": [24.4, 24.8, 24.8, 24.4, 24.4],
        "lon": [68.6, 68.6, 69.1, 69.1, 68.6],
        "depth": 3.5,
        "center": [24.66, 68.84]
    },
    "Thatta": {
        "lat": [24.5, 24.9, 24.9, 24.5, 24.5],
        "lon": [67.7, 67.7, 68.2, 68.2, 67.7],
        "depth": 2.2,
        "center": [24.75, 67.92]
    },
    "Jamshoro": {
        "lat": [25.2, 25.6, 25.6, 25.2, 25.2],
        "lon": [68.0, 68.0, 68.5, 68.5, 68.0],
        "depth": 1.4,
        "center": [25.43, 68.28]
    }
}

# Convert to DataFrame for easy access
df = pd.DataFrame([
    {"District": name, "depth": data["depth"], 
     "lat": data["center"][0], "lon": data["center"][1]}
    for name, data in district_boundaries.items()
])

# ================== SIDEBAR ==================
st.sidebar.header("Options")
color_scale = st.sidebar.selectbox(
    "Color Scale",
    ["YlOrRd", "Reds", "OrRd", "Hot", "Viridis", "Plasma", "RdYlBu_r"]
)
show_labels = st.sidebar.checkbox("Show District Labels", True)

# ================== METRICS ==================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Max Depth", f"{df['depth'].max():.1f} m")
with col2:
    st.metric("Most Affected", df.loc[df['depth'].idxmax(), 'District'])
with col3:
    st.metric("Districts", len(df))

# ================== CHOROPLETH MAP (NO JSON NEEDED) ==================
st.subheader("District-wise Flood Depth Map")

fig = go.Figure()

# Add each district as a separate polygon
for district_name, boundary in district_boundaries.items():
    fig.add_trace(go.Scattergeo(
        lon=boundary["lon"],
        lat=boundary["lat"],
        fill="toself",
        fillcolor=None,  # Will be set by marker.colorscale
        mode="lines",
        line=dict(color="black", width=1),
        name=district_name,
        text=f"{district_name}<br>Depth: {boundary['depth']}m",
        hoverinfo="text",
        marker=dict(
            color=boundary["depth"],
            colorscale=color_scale,
            showscale=True if district_name == list(district_boundaries.keys())[0] else False,
            cmin=0,
            cmax=df['depth'].max(),
            colorbar=dict(
                title="Depth (m)",
                thickness=20,
                len=0.5,
                x=1.02
            ) if district_name == list(district_boundaries.keys())[0] else None
        )
    ))

# Add district center points with labels
if show_labels:
    fig.add_trace(go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df['District'],
        mode='text',
        textfont=dict(size=10, color='black', family='Arial'),
        showlegend=False,
        hoverinfo='none'
    ))

fig.update_layout(
    height=700,
    margin={"r":50,"t":30,"l":0,"b":0},
    geo=dict(
        scope='asia',
        projection_type='mercator',
        showland=True,
        landcolor='rgb(240, 240, 240)',
        coastlinecolor='gray',
        showcountries=True,
        countrycolor='gray',
        showsubunits=True,
        subunitcolor='lightgray',
        center=dict(lat=26.5, lon=68.5),
        lonaxis_range=[66, 71],
        lataxis_range=[24, 29]
    ),
    title="Sindh Districts - Flood Depth"
)

st.plotly_chart(fig, use_container_width=True)

# ================== BAR CHART ==================
st.subheader("Flood Depth by District")
fig_bar = px.bar(
    df.sort_values('depth', ascending=True),
    y='District',
    x='depth',
    orientation='h',
    color='depth',
    color_continuous_scale=color_scale,
    labels={'depth': 'Depth (m)'},
    height=500
)
fig_bar.update_layout(
    xaxis_title="Depth (meters)",
    yaxis_title=""
)
st.plotly_chart(fig_bar, use_container_width=True)

# ================== TABLE ==================
st.subheader("District Data")
st.dataframe(
    df[['District', 'depth']].sort_values('depth', ascending=False),
    column_config={
        "District": "District",
        "depth": st.column_config.NumberColumn("Depth (m)", format="%.1f")
    },
    hide_index=True,
    use_container_width=True
)

# ================== SUMMARY ==================
with st.expander("📊 Summary Statistics"):
    st.write(f"**Total Districts:** {len(df)}")
    st.write(f"**Average Depth:** {df['depth'].mean():.2f} m")
    st.write(f"**Median Depth:** {df['depth'].median():.2f} m")
    st.write(f"**Standard Deviation:** {df['depth'].std():.2f} m")

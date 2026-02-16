import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Sindh Flood Analysis", layout="wide")

st.title("🌊 Sindh Flood Monitoring")
st.markdown("District-wise flood extent and depth analysis")

# ================== DISTRICT DATA ==================
districts_data = {
    "District": ["Karachi", "Hyderabad", "Sukkur", "Larkana", "Dadu", 
                 "Jacobabad", "Shikarpur", "Khairpur", "Nawabshah", 
                 "Mirpurkhas", "Umerkot", "Tharparkar", "Badin", "Thatta", "Jamshoro"],
    "Latitude": [24.86, 25.38, 27.70, 27.56, 26.73, 28.28, 27.96, 27.53, 
                 26.24, 25.53, 25.36, 24.89, 24.66, 24.75, 25.43],
    "Longitude": [67.01, 68.37, 68.87, 68.21, 67.78, 68.44, 68.65, 68.76, 
                  68.41, 69.02, 69.74, 70.20, 68.84, 67.92, 68.28],
    "Extent_km2": [450, 380, 520, 290, 610, 180, 320, 275, 490, 340, 210, 150, 580, 420, 310],
    "Depth_m": [2.5, 1.8, 3.2, 1.2, 4.0, 0.8, 1.5, 1.1, 2.8, 1.6, 0.9, 0.5, 3.5, 2.2, 1.4]
}

df = pd.DataFrame(districts_data)

# ================== SIDEBAR CONTROLS ==================
st.sidebar.header("Filters")

# Color selector
color_var = st.sidebar.radio(
    "Color Map By:",
    ["Depth_m", "Extent_km2"],
    format_func=lambda x: "Flood Depth (m)" if x == "Depth_m" else "Flood Extent (km²)"
)

# Size selector
size_var = st.sidebar.radio(
    "Size Points By:",
    ["Extent_km2", "Depth_m"],
    format_func=lambda x: "Flood Extent (km²)" if x == "Extent_km2" else "Flood Depth (m)"
)

# Filter sliders
min_extent = st.sidebar.slider("Min Extent (km²)", 0, 700, 0)
min_depth = st.sidebar.slider("Min Depth (m)", 0.0, 5.0, 0.0)

# Filter data
filtered_df = df[(df['Extent_km2'] >= min_extent) & (df['Depth_m'] >= min_depth)]

# ================== METRICS ==================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Districts", len(df))
with col2:
    st.metric("Affected Districts", len(filtered_df))
with col3:
    st.metric("Total Flood Extent", f"{filtered_df['Extent_km2'].sum():,} km²")
with col4:
    st.metric("Max Depth", f"{filtered_df['Depth_m'].max():.1f} m")

# ================== MAIN MAP ==================
st.subheader("🗺️ Flood Impact Map")

# Create the map
fig = go.Figure()

# Add scatter mapbox for better visualization
fig.add_trace(go.Scattermapbox(
    lat=filtered_df['Latitude'],
    lon=filtered_df['Longitude'],
    mode='markers+text',
    marker=dict(
        size=filtered_df[size_var] * 2,  # Scale size
        color=filtered_df[color_var],
        colorscale='Reds',
        showscale=True,
        colorbar=dict(
            title="Flood Depth (m)" if color_var == "Depth_m" else "Extent (km²)",
            thickness=20,
            len=0.5
        ),
        cmin=filtered_df[color_var].min(),
        cmax=filtered_df[color_var].max(),
        opacity=0.8,
        line=dict(width=1, color='black')
    ),
    text=filtered_df['District'],
    textposition="top center",
    textfont=dict(size=10, color='black'),
    hoverinfo='text',
    hovertext=[
        f"<b>{d}</b><br>" +
        f"Extent: {e:.0f} km²<br>" +
        f"Depth: {dp:.1f} m"
        for d, e, dp in zip(filtered_df['District'], 
                           filtered_df['Extent_km2'], 
                           filtered_df['Depth_m'])
    ]
))

# Update layout
fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=dict(lat=26.5, lon=68.5),
        zoom=6
    ),
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ================== EXTENT CHART ==================
st.subheader("📊 Flood Extent by District")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # Extent bar chart
    fig_extent = px.bar(
        filtered_df.sort_values('Extent_km2', ascending=True),
        y='District',
        x='Extent_km2',
        orientation='h',
        title="Flood Extent (km²)",
        color='Extent_km2',
        color_continuous_scale='Reds',
        text='Extent_km2'
    )
    fig_extent.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_extent.update_layout(height=400, xaxis_title="Extent (km²)", yaxis_title="")
    st.plotly_chart(fig_extent, use_container_width=True)

with col_chart2:
    # Depth bar chart
    fig_depth = px.bar(
        filtered_df.sort_values('Depth_m', ascending=True),
        y='District',
        x='Depth_m',
        orientation='h',
        title="Flood Depth (m)",
        color='Depth_m',
        color_continuous_scale='Blues',
        text='Depth_m'
    )
    fig_depth.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_depth.update_layout(height=400, xaxis_title="Depth (m)", yaxis_title="")
    st.plotly_chart(fig_depth, use_container_width=True)

# ================== DETAILED TABLE ==================
st.subheader("📋 District Details")

# Format the dataframe for display
display_df = filtered_df[['District', 'Extent_km2', 'Depth_m']].copy()
display_df.columns = ['District', 'Extent (km²)', 'Depth (m)']
display_df = display_df.sort_values('Extent (km²)', ascending=False)

# Add a severity column
display_df['Severity'] = pd.cut(
    display_df['Depth (m)'],
    bins=[0, 1, 2, 3, 5],
    labels=['Low', 'Moderate', 'High', 'Severe']
)

st.dataframe(
    display_df,
    column_config={
        "District": "District",
        "Extent (km²)": st.column_config.NumberColumn(format="%.0f"),
        "Depth (m)": st.column_config.NumberColumn(format="%.1f"),
        "Severity": st.column_config.Column("Risk Level")
    },
    use_container_width=True,
    hide_index=True
)

# ================== SUMMARY STATISTICS ==================
with st.expander("📈 Summary Statistics"):
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.write("**Extent Statistics (km²)**")
        st.write(f"Mean: {filtered_df['Extent_km2'].mean():.1f}")
        st.write(f"Median: {filtered_df['Extent_km2'].median():.1f}")
        st.write(f"Std Dev: {filtered_df['Extent_km2'].std():.1f}")
        st.write(f"Total: {filtered_df['Extent_km2'].sum():.0f}")
    
    with col_stat2:
        st.write("**Depth Statistics (m)**")
        st.write(f"Mean: {filtered_df['Depth_m'].mean():.2f}")
        st.write(f"Median: {filtered_df['Depth_m'].median():.2f}")
        st.write(f"Std Dev: {filtered_df['Depth_m'].std():.2f}")
        st.write(f"Max: {filtered_df['Depth_m'].max():.2f}")

# ================== DOWNLOAD BUTTON ==================
csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Data as CSV",
    data=csv,
    file_name="sindh_flood_data.csv",
    mime="text/csv"
)

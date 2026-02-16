import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json

st.set_page_config(page_title="Sindh Flood Analysis", layout="wide")

st.title("🌊 Sindh Flood Monitoring")
st.markdown("District-wise flood extent and depth analysis with administrative boundary")

# ================== LOAD SINDH BOUNDARY ==================
try:
    with open("Sindh.geojson") as f:
        sindh_geo = json.load(f)
    st.sidebar.success("✅ Sindh boundary loaded")
except:
    st.sidebar.error("❌ Sindh.geojson not found")
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
st.subheader("🗺️ Flood Impact Map with Sindh Boundary")

fig = go.Figure()

# Add Sindh boundary if available
if sindh_geo and show_boundary:
    for feature in sindh_geo['features']:
        if feature['geometry']['type'] == 'Polygon':
            coords = feature['geometry']['coordinates'][0]
            lon, lat = zip(*coords)
            fig.add_trace(go.Scattergeo(
                lon=lon,
                lat=lat,
                mode='lines',
                line=dict(color='black', width=2),
                name='Sindh Boundary',
                showlegend=False
            ))
        elif feature['geometry']['type'] == 'MultiPolygon':
            for polygon in feature['geometry']['coordinates']:
                coords = polygon[0]
                lon, lat = zip(*coords)
                fig.add_trace(go.Scattergeo(
                    lon=lon,
                    lat=lat,
                    mode='lines',
                    line=dict(color='black', width=2),
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
        size=filtered_df['Extent'] / 8,
        color=filtered_df['Depth'],
        colorscale='Reds',
        showscale=True,
        colorbar=dict(
            title="Depth (m)",
            x=1.05,
            len=0.5,
            tickvals=[0, 1, 2, 3, 4],
            ticktext=['Low', 'Moderate', 'High', 'Severe', 'Extreme']
        ),
        line=dict(width=1, color='black'),
        sizemode='area',
        sizeref=2.*max(filtered_df['Extent'])/(40.**2),
        cmin=0,
        cmax=4
    ),
    textposition="top center",
    textfont=dict(size=10, color='black', family='Arial Black'),
    hoverinfo='text',
    hovertext=[
        f"<b>{d}</b><br>" +
        f"Extent: {e:.0f} km²<br>" +
        f"Depth: {dp:.1f} m"
        for d, e, dp in zip(filtered_df['District'], 
                           filtered_df['Extent'], 
                           filtered_df['Depth'])
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
    margin=dict(l=0, r=50, t=30, b=0),
    title=dict(text="Sindh Province - Flood Affected Areas", x=0.5)
)

st.plotly_chart(fig, use_container_width=True)

# ================== EXTENT & DEPTH CHARTS ==================
st.subheader("📊 Flood Analysis by District")

col1, col2 = st.columns(2)

with col1:
    fig_extent = px.bar(
        filtered_df.sort_values('Extent'),
        y='District',
        x='Extent',
        orientation='h',
        title="Flood Extent (km²)",
        color='Extent',
        color_continuous_scale='Reds',
        text='Extent'
    )
    fig_extent.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_extent.update_layout(height=400, xaxis_title="Square Kilometers", yaxis_title="")
    st.plotly_chart(fig_extent, use_container_width=True)

with col2:
    fig_depth = px.bar(
        filtered_df.sort_values('Depth'),
        y='District',
        x='Depth',
        orientation='h',
        title="Flood Depth (meters)",
        color='Depth',
        color_continuous_scale='Blues',
        text='Depth'
    )
    fig_depth.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_depth.update_layout(height=400, xaxis_title="Meters", yaxis_title="")
    st.plotly_chart(fig_depth, use_container_width=True)

# ================== DATA TABLE ==================
st.subheader("📋 District Summary")

display_df = filtered_df[['District', 'Extent', 'Depth']].copy()
display_df.columns = ['District', 'Extent (km²)', 'Depth (m)']
display_df = display_df.sort_values('Extent (km²)', ascending=False)

def get_severity(depth):
    if depth >= 3.0:
        return "🔴 SEVERE"
    elif depth >= 2.0:
        return "🟠 HIGH"
    elif depth >= 1.0:
        return "🟡 MODERATE"
    else:
        return "🟢 LOW"

display_df['Risk Level'] = display_df['Depth (m)'].apply(get_severity)

st.dataframe(
    display_df,
    column_config={
        "District": "District",
        "Extent (km²)": st.column_config.NumberColumn(format="%.0f km²"),
        "Depth (m)": st.column_config.NumberColumn(format="%.1f m"),
        "Risk Level": "Flood Risk"
    },
    use_container_width=True,
    hide_index=True
)

# ================== STATISTICS ==================
with st.expander("📈 Summary Statistics"):
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.write("**🌊 Extent Statistics (km²)**")
        st.write(f"• Mean: {filtered_df['Extent'].mean():.1f}")
        st.write(f"• Median: {filtered_df['Extent'].median():.1f}")
        st.write(f"• Maximum: {filtered_df['Extent'].max():.0f}")
        st.write(f"• Minimum: {filtered_df['Extent'].min():.0f}")
        st.write(f"• Total: {filtered_df['Extent'].sum():.0f}")
    
    with col_stat2:
        st.write("**📏 Depth Statistics (m)**")
        st.write(f"• Mean: {filtered_df['Depth'].mean():.2f}")
        st.write(f"• Median: {filtered_df['Depth'].median():.2f}")
        st.write(f"• Maximum: {filtered_df['Depth'].max():.1f}")
        st.write(f"• Minimum: {filtered_df['Depth'].min():.1f}")
        st.write(f"• Std Dev: {filtered_df['Depth'].std():.2f}")

# ================== TOP AFFECTED DISTRICTS ==================
st.subheader("🏆 Most Affected Districts")
top3 = filtered_df.nlargest(3, 'Depth')[['District', 'Depth', 'Extent']]
cols = st.columns(3)
for i, (idx, row) in enumerate(top3.iterrows()):
    with cols[i]:
        st.info(f"**#{i+1} {row['District']}**")
        st.write(f"Depth: {row['Depth']:.1f} m")
        st.write(f"Extent: {row['Extent']:.0f} km²")

# ================== DOWNLOAD BUTTON ==================
csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Data as CSV",
    data=csv,
    file_name="sindh_flood_data.csv",
    mime="text/csv"
)

# ================== BOUNDARY VERIFICATION ==================
with st.expander("🗺️ View Sindh Boundary Only"):
    if sindh_geo:
        fig2 = px.choropleth_mapbox(
            geojson=sindh_geo,
            locations=["Sindh"],
            featureidkey="properties.name",
            color=[1],
            mapbox_style="carto-positron",
            center={"lat": 26.5, "lon": 68.5},
            zoom=5,
            opacity=0.3
        )
        fig2.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Sindh provincial boundary for reference")
    else:
        st.error("Boundary file not available")

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
    "Lat": [24.86, 25.38, 27.70, 27.56, 26.73, 28.28, 27.96, 27.53, 
            26.24, 25.53, 25.36, 24.89, 24.66, 24.75, 25.43],
    "Lon": [67.01, 68.37, 68.87, 68.21, 67.78, 68.44, 68.65, 68.76, 
            68.41, 69.02, 69.74, 70.20, 68.84, 67.92, 68.28],
    "Extent": [450, 380, 520, 290, 610, 180, 320, 275, 490, 340, 210, 150, 580, 420, 310],
    "Depth": [2.5, 1.8, 3.2, 1.2, 4.0, 0.8, 1.5, 1.1, 2.8, 1.6, 0.9, 0.5, 3.5, 2.2, 1.4]
}

df = pd.DataFrame(districts_data)

# ================== SIDEBAR ==================
st.sidebar.header("Filters")

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
st.subheader("🗺️ Flood Impact Map")

fig = go.Figure()

# Add bubble map
fig.add_trace(go.Scattergeo(
    lon=filtered_df['Lon'],
    lat=filtered_df['Lat'],
    text=filtered_df['District'],
    mode='markers+text',
    marker=dict(
        size=filtered_df['Extent'] / 10,  # Scale size
        color=filtered_df['Depth'],
        colorscale='Reds',
        showscale=True,
        colorbar=dict(
            title="Depth (m)",
            x=1.05,
            len=0.5
        ),
        line=dict(width=1, color='black'),
        sizemode='area',
        sizeref=2.*max(filtered_df['Extent'])/(40.**2),
    ),
    textposition="top center",
    textfont=dict(size=10, color='black'),
    hovertemplate='<b>%{text}</b><br>' +
                  'Extent: %{marker.size:.0f} km²<br>' +
                  'Depth: %{marker.color:.1f} m' +
                  '<extra></extra>'
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
    height=600,
    margin=dict(l=0, r=50, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ================== EXTENT & DEPTH CHARTS ==================
st.subheader("📊 Flood Analysis")

col1, col2 = st.columns(2)

with col1:
    # Extent chart
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
    fig_extent.update_layout(height=400, xaxis_title="km²", showlegend=False)
    st.plotly_chart(fig_extent, use_container_width=True)

with col2:
    # Depth chart
    fig_depth = px.bar(
        filtered_df.sort_values('Depth'),
        y='District',
        x='Depth',
        orientation='h',
        title="Flood Depth (m)",
        color='Depth',
        color_continuous_scale='Blues',
        text='Depth'
    )
    fig_depth.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_depth.update_layout(height=400, xaxis_title="meters", showlegend=False)
    st.plotly_chart(fig_depth, use_container_width=True)

# ================== DATA TABLE ==================
st.subheader("📋 District Summary")

# Create display dataframe
display_df = filtered_df[['District', 'Extent', 'Depth']].copy()
display_df.columns = ['District', 'Extent (km²)', 'Depth (m)']
display_df = display_df.sort_values('Extent (km²)', ascending=False)

# Add severity classification
def get_severity(depth):
    if depth >= 3.0:
        return "🔴 Severe"
    elif depth >= 2.0:
        return "🟠 High"
    elif depth >= 1.0:
        return "🟡 Moderate"
    else:
        return "🟢 Low"

display_df['Severity'] = display_df['Depth (m)'].apply(get_severity)

st.dataframe(
    display_df,
    column_config={
        "District": "District",
        "Extent (km²)": st.column_config.NumberColumn(format="%.0f"),
        "Depth (m)": st.column_config.NumberColumn(format="%.1f"),
        "Severity": "Risk Level"
    },
    use_container_width=True,
    hide_index=True
)

# ================== STATISTICS ==================
with st.expander("📈 Summary Statistics"):
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.write("**Extent Statistics (km²)**")
        st.write(f"Mean: {filtered_df['Extent'].mean():.1f}")
        st.write(f"Median: {filtered_df['Extent'].median():.1f}")
        st.write(f"Max: {filtered_df['Extent'].max():.0f}")
        st.write(f"Min: {filtered_df['Extent'].min():.0f}")
    
    with col_stat2:
        st.write("**Depth Statistics (m)**")
        st.write(f"Mean: {filtered_df['Depth'].mean():.2f}")
        st.write(f"Median: {filtered_df['Depth'].median():.2f}")
        st.write(f"Max: {filtered_df['Depth'].max():.1f}")
        st.write(f"Min: {filtered_df['Depth'].min():.1f}")

# ================== TOP AFFECTED ==================
st.subheader("🏆 Most Affected Districts")
top3 = filtered_df.nlargest(3, 'Depth')[['District', 'Depth', 'Extent']]
cols = st.columns(3)
for i, (idx, row) in enumerate(top3.iterrows()):
    with cols[i]:
        st.success(f"**{i+1}. {row['District']}**")
        st.write(f"Depth: {row['Depth']:.1f} m")
        st.write(f"Extent: {row['Extent']:.0f} km²")

# ================== DOWNLOAD ==================
csv = display_df.to_csv(index=False)
st.download_button(
    label="📥 Download Data",
    data=csv,
    file_name="sindh_flood_data.csv",
    mime="text/csv"
)

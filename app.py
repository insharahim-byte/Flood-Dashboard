import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Sindh District Flood Map", layout="wide")

st.title("🌊 Sindh Flood Map (District Level – Test Run)")
st.markdown("US-style filled district map (approx boundaries, no files)")

# ================== DISTRICT DATA ==================
data = pd.DataFrame({
    "District": ["Karachi", "Hyderabad", "Sukkur", "Larkana", "Nawabshah", "Mirpurkhas"],
    "Severity": [4, 3, 2, 3, 2, 1]
})

# ================== DISTRICT POLYGONS (approx) ==================
district_shapes = {
    "Karachi": ([24.6, 24.9, 25.1, 24.8], [66.8, 67.3, 67.0, 66.7]),
    "Hyderabad": ([25.2, 25.6, 25.8, 25.4], [68.0, 68.4, 68.1, 67.8]),
    "Sukkur": ([27.4, 27.9, 28.1, 27.6], [68.5, 69.0, 68.7, 68.3]),
    "Larkana": ([27.3, 27.8, 28.0, 27.5], [67.5, 68.0, 67.7, 67.2]),
    "Nawabshah": ([26.0, 26.4, 26.6, 26.2], [68.0, 68.5, 68.2, 67.8]),
    "Mirpurkhas": ([25.2, 25.6, 25.8, 25.4], [69.0, 69.4, 69.1, 68.7]),
}

# ================== COLOR SCALE ==================
def get_color(val):
    if val == 4:
        return "darkred"
    elif val == 3:
        return "red"
    elif val == 2:
        return "orange"
    else:
        return "yellow"

# ================== MAP ==================
fig = go.Figure()

for _, row in data.iterrows():
    lats, lons = district_shapes[row["District"]]
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        fill="toself",
        name=row["District"],
        text=f"{row['District']}<br>Severity: {row['Severity']}",
        hoverinfo="text",
        fillcolor=get_color(row["Severity"]),
        line=dict(color="black", width=1),
        opacity=0.75
    ))

fig.update_layout(
    title="Sindh Flood Severity by District (Test Boundaries)",
    geo=dict(
        scope="asia",
        center=dict(lat=26.5, lon=68.5),
        lonaxis_range=[66, 70],
        lataxis_range=[24, 29],
        projection_type="natural earth",
        showland=True,
        landcolor="rgb(240,240,240)",
        showcountries=True,
        countrycolor="gray",
    ),
    height=650,
    margin=dict(l=0, r=0, t=50, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# ================== TABLE ==================
st.subheader("District Flood Severity")
st.dataframe(data)

st.caption("⚠️ District boundaries are approximate for testing only.")

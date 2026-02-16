import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Sindh Flood Severity Map", layout="wide")

st.title("🌊 Sindh Flood Severity Dashboard")
st.markdown("US-style choropleth map for Sindh districts (yellow → red).")

# ================== LOAD GEOJSON ==================
with open("data/sindh_districts.geojson") as f:
    sindh_geojson = json.load(f)

# ================== FLOOD DATA ==================
data = {
    "Karachi": 2.5,
    "Hyderabad": 1.8,
    "Sukkur": 3.2,
    "Larkana": 1.2,
    "Dadu": 4.0,
    "Jacobabad": 0.8,
    "Shikarpur": 1.5,
    "Khairpur": 1.1,
    "Nawabshah": 2.8,
    "Mirpurkhas": 1.6,
    "Umerkot": 0.9,
    "Tharparkar": 0.5,
    "Badin": 3.5,
    "Thatta": 2.2,
    "Jamshoro": 1.4,
}

df = pd.DataFrame(list(data.items()), columns=["District", "Depth"])

# ================== CLASSIFICATION ==================
def classify(depth):
    if depth < 1:
        return "Low"
    elif depth < 2:
        return "Moderate"
    elif depth < 3:
        return "High"
    else:
        return "Severe"

df["Severity"] = df["Depth"].apply(classify)

color_map = {
    "Low": "#ffffb2",
    "Moderate": "#fecc5c",
    "High": "#fd8d3c",
    "Severe": "#e31a1c"
}

# ================== CHOROPLETH MAP ==================
fig = px.choropleth(
    df,
    geojson=sindh_geojson,
    locations="District",
    featureidkey="properties.NAME_2",  # must match GeoJSON field
    color="Severity",
    color_discrete_map=color_map,
    hover_name="District",
    hover_data={"Depth": True},
    projection="natural earth",
)

fig.update_geos(
    fitbounds="locations",
    visible=False
)

fig.update_layout(
    height=700,
    margin=dict(l=0, r=0, t=40, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# ================== BAR CHART ==================
st.subheader("Flood Depth by District")

fig_bar = px.bar(
    df.sort_values("Depth", ascending=False),
    x="District",
    y="Depth",
    color="Severity",
    color_discrete_map=color_map
)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# ================== TABLE ==================
st.subheader("District Flood Data")
st.dataframe(df)

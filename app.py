import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sindh Flood Severity Map", layout="wide")

st.title("🌊 Sindh Flood Severity Dashboard")
st.markdown("Map styled after severity maps (yellow → red like template image).")

# ================== DATA ==================
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

df = pd.DataFrame.from_dict(districts, orient="index").reset_index()
df.rename(columns={"index": "District"}, inplace=True)

# ================== CLASSIFY LIKE TEMPLATE ==================
def classify(depth):
    if depth < 1:
        return "Low"
    elif depth < 2:
        return "Moderate"
    elif depth < 3:
        return "High"
    else:
        return "Severe"

df["Severity"] = df["depth"].apply(classify)

color_map = {
    "Low": "#ffffb2",
    "Moderate": "#fecc5c",
    "High": "#fd8d3c",
    "Severe": "#e31a1c"
}

# ================== MAP ==================
st.subheader("Flood Severity Map (Template Style)")

fig = px.scatter_geo(
    df,
    lat="lat",
    lon="lon",
    color="Severity",
    color_discrete_map=color_map,
    hover_name="District",
    hover_data={"depth": True},
    size="depth",
    size_max=18,
)

fig.update_layout(
    geo=dict(
        scope="asia",
        center=dict(lat=26.5, lon=68.5),
        lonaxis_range=[66, 71],
        lataxis_range=[24, 29],
        projection_type="natural earth",
        showcountries=True,
        countrycolor="black",
        showsubunits=True,
        subunitcolor="gray",
        bgcolor="rgba(0,0,0,0)"
    ),
    height=700,
    margin=dict(l=0, r=0, t=30, b=0),
)

st.plotly_chart(fig, use_container_width=True)

# ================== BAR ==================
st.subheader("Flood Depth by District")

fig_bar = px.bar(
    df.sort_values("depth", ascending=False),
    x="District",
    y="depth",
    color="Severity",
    color_discrete_map=color_map
)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# ================== TABLE ==================
st.subheader("District Flood Data")
st.dataframe(df[["District", "depth", "Severity"]])

import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium

# === load your schools and addresses
@st.cache_data
def load_schools():
    return pd.read_csv("https://raw.githubusercontent.com/alanrrz/la_buffer_app_clean/ab73deb13c0a02107f43001161ab70891630a9c7/schools.csv")

st.title("📍 Construction Impact Map Generator")
st.caption("Generate an interactive map with a red impact zone & entrance marker")

schools = load_schools()
schools.columns = schools.columns.str.strip()
site_list = schools["LABEL"].sort_values().tolist()
site_selected = st.selectbox("Select Campus", site_list)

radius = st.slider("Radius around school (meters)", 100, 1000, 300, 50)

if st.button("Generate Map"):
    with st.spinner("Generating map…"):
        row = schools[schools["LABEL"] == site_selected].iloc[0]
        lon, lat = row["LON"], row["LAT"]

        m = folium.Map(location=[lat, lon], zoom_start=16, tiles="cartodbpositron")

        # Impact zone as a red circle
        folium.Circle(
            location=[lat, lon],
            radius=radius,
            color="darkred",
            fill=True,
            fill_color="red",
            fill_opacity=0.4,
        ).add_to(m)

        # Entrance marker with star icon
        folium.Marker(
            location=[lat, lon],
            tooltip="Entrance",
            icon=folium.Icon(color="red", icon="star", prefix="fa"),
        ).add_to(m)

        st_data = st_folium(m, width=700, height=500)

        # Optional export of the map as HTML and PNG (requires selenium)
        html_data = m.get_root().render()
        st.download_button(
            "Download HTML", data=html_data,
            file_name=f"{site_selected.replace(' ', '_')}.html", mime="text/html"
        )

        try:
            png_data = m._to_png(5)
            st.download_button(
                "Download PNG", data=png_data,
                file_name=f"{site_selected.replace(' ', '_')}.png", mime="image/png"
            )
        except Exception as e:
            st.info("PNG export requires selenium and a compatible web driver.")

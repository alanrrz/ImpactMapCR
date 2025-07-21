import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# === load your schools and addresses
@st.cache_data
def load_schools():
    return pd.read_csv("https://raw.githubusercontent.com/alanrrz/la_buffer_app_clean/ab73deb13c0a02107f43001161ab70891630a9c7/schools.csv")

st.title("📍 Construction Impact Map Generator")
st.caption("Generate a black & white map with a red impact zone & entrance marker")

schools = load_schools()
schools.columns = schools.columns.str.strip()
site_list = schools["LABEL"].sort_values().tolist()
site_selected = st.selectbox("Select Campus", site_list)

radius = st.slider("Radius around school (meters)", 100, 1000, 300, 50)

if st.button("Generate Map"):
    with st.spinner("Generating map…"):
        row = schools[schools["LABEL"] == site_selected].iloc[0]
        lon, lat = row["LON"], row["LAT"]
        center = (lon, lat)

        # Create GeoSeries
        point = Point(lon, lat)
        buffer = gpd.GeoSeries([point], crs='EPSG:4326').to_crs(epsg=3857).buffer(radius)

        fig, ax = plt.subplots(figsize=(8,8))

        # black & white base
        buffer.to_crs(epsg=4326).plot(ax=ax, color='red', alpha=0.4, edgecolor='darkred', label='Impact Zone')
        gpd.GeoSeries([point], crs='EPSG:4326').plot(ax=ax, color='blue', marker='*', markersize=100, label='Entrance')

        ax.annotate("School Entrance", xy=(lon, lat), xytext=(lon+0.001, lat+0.001),
                    arrowprops=dict(facecolor='black', arrowstyle="->"), fontsize=9)

        plt.axis('off')
        plt.title(f"Construction Impact Map – {site_selected}", fontsize=12)

        from io import BytesIO
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        buf.seek(0)

        st.pyplot(fig)
        st.download_button("Download PNG", data=buf, file_name=f"{site_selected.replace(' ','_')}_impact_map.png", mime="image/png")

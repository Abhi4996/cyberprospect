import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from utils.db import get_connection

st.set_page_config(page_title="Geo Map | CyberProspect", page_icon="🌍", layout="wide")

st.title("🌍 Global Risk Exposure")
st.markdown("Visualize the physical locations of exposed infrastructure.")

@st.cache_data(show_spinner="Loading geographic map data...")
def load_geo_data():
    conn = get_connection()
    try:
        # Load up to 1000 highest risk IPs with location data
        df = conn.execute("""
            SELECT 
                ip_str, port, org, ip_risk_score, latitude, longitude, city, country_name
            FROM scans
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
              AND is_excluded = FALSE
            ORDER BY ip_risk_score DESC
            LIMIT 1000
        """).fetchdf()
        return df
    except Exception as e:
        st.error(f"Error loading map data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

df = load_geo_data()

if df.empty:
    st.warning("No geographic data available.")
else:
    # Filter slider
    min_score = st.slider("Filter by minimum IP Risk Score", 0, 100, 10)
    filtered_df = df[df['ip_risk_score'] >= min_score]
    
    st.write(f"Showing **{len(filtered_df)}** exposed endpoints.")
    
    from folium.plugins import MarkerCluster
    
    # Base map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
    
    # Add Marker Cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers
    for idx, row in filtered_df.iterrows():
        # Color based on risk
        color = "red" if row['ip_risk_score'] >= 50 else "orange" if row['ip_risk_score'] >= 20 else "blue"
        
        popup_html = f"""
        <b>Org:</b> {row['org']}<br>
        <b>IP:</b> {row['ip_str']}:{row['port']}<br>
        <b>Risk Score:</b> {row['ip_risk_score']}<br>
        <b>Location:</b> {row['city']}, {row['country_name']}
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(marker_cluster)
        
    folium_static(m, width=1200, height=600)

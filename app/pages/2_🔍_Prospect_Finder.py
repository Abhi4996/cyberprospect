import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
import pandas as pd
from utils.db import get_connection

st.set_page_config(page_title="Prospect Finder | CyberProspect", page_icon="🔍", layout="wide")

st.title("🔍 Prospect Finder")
st.markdown("Filter and identify target organizations based on their security posture.")

# Sidebar filters
st.sidebar.header("Filters")

min_score = st.sidebar.slider("Minimum Risk Score", 0, 100, 20)
min_ips = st.sidebar.slider("Minimum IPs Exposed", 1, 1000, 1)

def load_prospects(min_s, min_i):
    conn = get_connection()
    try:
        df = conn.execute(f"""
            SELECT 
                org as Organization,
                ROUND(combined_risk_score, 1) as "Risk Score",
                total_ips as "Total IPs",
                total_open_ports as "Open Ports",
                list_extract(countries, 1) as "Primary Location"
            FROM org_scores
            WHERE combined_risk_score >= {min_s}
              AND total_ips >= {min_i}
            ORDER BY combined_risk_score DESC
        """).fetchdf()
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

df = load_prospects(min_score, min_ips)

if df.empty:
    st.info("No prospects found matching these criteria or data not loaded.")
else:
    st.write(f"Found **{len(df)}** target organizations.")
    
    # Use dataframe formatting
    st.dataframe(
        df,
        column_config={
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score", help="Composite risk score", format="%.1f", min_value=0, max_value=100
            ),
        },
        width="stretch",
        hide_index=True
    )
    
    st.markdown("---")
    st.markdown("### Next Steps")
    st.markdown("Note the **Organization** name above and navigate to **🏢 Company Deep Dive** to analyze their specific vulnerabilities and generate a sales pitch.")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
import plotly.express as px
from utils.db import get_connection

st.set_page_config(page_title="Dashboard | CyberProspect", page_icon="🏠", layout="wide")

st.title("🏠 Executive Dashboard")

def load_kpis():
    conn = get_connection()
    try:
        # Check if table exists
        tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
        if 'org_scores' not in tables:
            return None, None
            
        kpis = conn.execute("""
            SELECT 
                COUNT(DISTINCT org) as total_orgs,
                SUM(total_ips) as total_ips,
                AVG(combined_risk_score) as avg_score,
                COUNT(CASE WHEN max_risk_score > 50 THEN 1 END) as high_risk_orgs
            FROM org_scores
        """).fetchdf()
        
        top_orgs = conn.execute("""
            SELECT org, combined_risk_score, total_ips, total_open_ports
            FROM org_scores
            ORDER BY combined_risk_score DESC
            LIMIT 10
        """).fetchdf()
        
        return kpis, top_orgs
    except Exception as e:
        st.error(f"Database error: {e}")
        return None, None
    finally:
        conn.close()

kpis, top_orgs = load_kpis()

if kpis is None:
    st.warning("No data available. Please run the ETL pipeline first.")
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Target Organizations", f"{int(kpis['total_orgs'][0]):,}")
with col2:
    st.metric("Total IPs Scanned", f"{int(kpis['total_ips'][0]):,}")
with col3:
    st.metric("High Risk Orgs (>50)", f"{int(kpis['high_risk_orgs'][0]):,}")
with col4:
    st.metric("Avg Risk Score", f"{kpis['avg_score'][0]:.1f}/100")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Highest Risk Prospects")
    fig = px.bar(
        top_orgs.sort_values('combined_risk_score', ascending=True), 
        x="combined_risk_score", 
        y="org", 
        orientation='h',
        color="combined_risk_score",
        color_continuous_scale="Reds",
        hover_data=["total_ips", "total_open_ports"]
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)", 
        font_color="white",
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="white"
        )
    )
    st.plotly_chart(fig, width="stretch")

with col_right:
    st.subheader("Risk Score Distribution")
    # Fetch distribution
    conn = get_connection()
    dist = conn.execute("SELECT combined_risk_score FROM org_scores").fetchdf()
    conn.close()
    
    fig2 = px.histogram(
        dist, x="combined_risk_score", nbins=20,
        color_discrete_sequence=['#ef4444']
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)", 
        font_color="white",
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="white"
        )
    )
    st.plotly_chart(fig2, width="stretch")

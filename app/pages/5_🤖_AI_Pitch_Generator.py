import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
import pandas as pd
from utils.db import get_connection
from utils.llm import generate_pitch

st.set_page_config(page_title="AI Pitch Generator | CyberProspect", page_icon="🤖", layout="wide")

st.title("🤖 AI Sales Pitch Generator")
st.markdown("Generate hyper-personalized outreach emails using Gemini 3.1 Flash based on actual network exposure.")

# Sidebar API Key
# Attempts to load a default key from environment or streamlit secrets, otherwise remains blank
default_api_key = os.environ.get("GEMINI_API_KEY", "")
if not default_api_key:
    try:
        import streamlit as st
        default_api_key = st.secrets.get("GEMINI_API_KEY", "")
    except:
        pass

api_key = st.sidebar.text_input(
    "Google AI Studio API Key", 
    value=default_api_key,
    type="password", 
    help="Get a free key at aistudio.google.com"
)

# Get Top 500 orgs
def get_top_orgs():
    conn = get_connection()
    try:
        # Get top 500 by risk score
        orgs = conn.execute("""
            SELECT org, combined_risk_score, total_ips, total_open_ports, countries
            FROM org_scores 
            WHERE combined_risk_score > 0
            ORDER BY combined_risk_score DESC 
            LIMIT 500
        """).fetchdf()
        return orgs
    except:
        return pd.DataFrame()
    finally:
        conn.close()

top_orgs = get_top_orgs()

if top_orgs.empty:
    st.warning("No eligible organizations found. Run ETL first.")
    st.stop()

# Select org
org_names = top_orgs['org'].tolist()
selected_org = st.selectbox("Select Target Organization (Top 500 only)", org_names)

if selected_org:
    # Customization options
    col1, col2 = st.columns(2)
    tone = col1.selectbox("Tone", ["Professional & Urgent", "Consultative & Helpful", "Direct & Technical"])
    focus = col2.selectbox("Focus Area", ["Compliance & Risk", "Cost of Breach", "Operational Resilience"])
    
    # Check cache first
    conn = get_connection()
    cached = None
    try:
        cached = conn.execute("SELECT pitch_text FROM ai_pitches WHERE org = ? AND tone = ? AND focus_area = ?", [selected_org, tone, focus]).fetchone()
    except:
        pass
    
    if cached:
        st.success("Loaded from cache!")
        st.markdown(cached[0])
        if st.button("Regenerate"):
            cached = None # Force regen
    
    if not cached:
        if st.button("Generate Pitch ✨", type="primary"):
            if not api_key:
                st.error("Please enter an API Key in the sidebar.")
            else:
                with st.spinner("Analyzing vulnerabilities and crafting pitch..."):
                    try:
                        # Gather context data
                        org_data = top_orgs[top_orgs['org'] == selected_org].iloc[0]
                        risk_score = f"{org_data['combined_risk_score']:.1f}"
                        locations = ", ".join(org_data['countries']) if isinstance(org_data['countries'], list) else str(org_data['countries'])
                        total_ips = org_data['total_ips']
                        
                        # Detailed data
                        details = conn.execute("""
                            SELECT port, product, version, ssl_expired, http_server
                            FROM scans WHERE org = ?
                        """, [selected_org]).fetchdf()
                        
                        open_ports = details['port'].unique().tolist()
                        services = details['product'].dropna().unique().tolist()
                        ssl_issues = "Expired Certs Found" if details['ssl_expired'].any() else "None"
                        
                        # Vulns
                        try:
                            vulns = conn.execute("""
                                SELECT v.cve_id, v.cvss 
                                FROM vulns v JOIN scans s ON v.ip_str = s.ip_str 
                                WHERE s.org = ?
                            """, [selected_org]).fetchdf()
                            cve_details = ", ".join([f"{row['cve_id']} (CVSS {row['cvss']})" for _, row in vulns.iterrows()]) if not vulns.empty else "No known CVEs"
                        except:
                            cve_details = "None identified"
                            
                        pitch = generate_pitch(
                            selected_org, risk_score, locations, total_ips, 
                            str(open_ports), cve_details, str(services), ssl_issues,
                            tone, focus, api_key
                        )
                        
                        st.markdown("### Generated Pitch")
                        st.markdown(pitch)
                        
                        # Cache it
                        conn.execute("""
                            INSERT OR REPLACE INTO ai_pitches (org, pitch_text, tone, focus_area)
                            VALUES (?, ?, ?, ?)
                        """, [selected_org, pitch, tone, focus])
                        
                    except Exception as e:
                        st.error(f"Error preparing data: {e}")
                    
    conn.close()

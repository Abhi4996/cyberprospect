import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st
from utils.db import get_connection

st.set_page_config(page_title="Company Deep Dive | CyberProspect", page_icon="🏢", layout="wide")

st.title("🏢 Company Deep Dive")

# Get list of orgs for dropdown
def get_org_list():
    conn = get_connection()
    try:
        orgs = conn.execute("SELECT org FROM org_scores ORDER BY combined_risk_score DESC").fetchdf()
        return orgs['org'].tolist()
    except:
        return []
    finally:
        conn.close()

org_list = get_org_list()
if not org_list:
    st.warning("No organizations available. Please run ETL.")
    st.stop()

selected_org = st.selectbox("Select Organization to Analyze", org_list)

if selected_org:
    conn = get_connection()
    try:
        # Load org summary
        summary = conn.execute("SELECT * FROM org_scores WHERE org = ?", [selected_org]).fetchdf().iloc[0]
        
        st.markdown(f"## {selected_org}")
        st.progress(summary['combined_risk_score'] / 100, text=f"Risk Score: {summary['combined_risk_score']:.1f}/100")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Exposed IPs", summary['total_ips'])
        col2.metric("Open Ports", summary['total_open_ports'])
        locs = summary['countries']
        import collections.abc
        if isinstance(locs, collections.abc.Iterable) and not isinstance(locs, (str, bytes)):
            loc_str = ", ".join(str(l) for l in locs if l is not None)
        else:
            loc_str = str(locs)
        col3.metric("Locations", loc_str)
        
        st.markdown("### 🔴 Exposed Infrastructure")
        
        # Load detailed IPs and ports
        details = conn.execute(f"""
            SELECT ip_str, port, transport, product, version, country_name, ip_risk_score, ssl_expired, http_server
            FROM scans 
            WHERE org = ?
            ORDER BY ip_risk_score DESC
        """, [selected_org]).fetchdf()
        
        st.dataframe(details, width="stretch", hide_index=True)
        
        # Load vulnerabilities if any
        try:
            vulns = conn.execute("""
                SELECT v.ip_str, v.port, v.cve_id, v.cvss, v.epss, v.cve_summary 
                FROM vulns v
                JOIN scans s ON v.ip_str = s.ip_str AND v.port = s.port
                WHERE s.org = ?
                ORDER BY v.cvss DESC
            """, [selected_org]).fetchdf()
            
            if not vulns.empty:
                st.markdown("### 🚨 Known Vulnerabilities (CVEs)")
                st.dataframe(vulns, width="stretch", hide_index=True)
        except:
            pass # No vulns table or no vulns
            
        st.markdown("---")
        st.markdown("### 🤖 Next Step: AI Sales Pitch")
        st.markdown(f"Ready to contact **{selected_org}**? Head over to the **AI Pitch Generator** page to craft a personalized outreach message based on these findings.")
        
    except Exception as e:
        st.error(f"Error loading details: {e}")
    finally:
        conn.close()

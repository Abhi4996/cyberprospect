import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

st.set_page_config(
    page_title="CyberProspect | Sales Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    /* Main theme adjustments */
    .stApp {
        background-color: #0f111a;
        color: #e2e8f0;
    }
    .css-1d391kg, .stSidebar {
        background-color: #1a1d2d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9, #2563eb);
        color: white;
        border: none;
        border-radius: 0.25rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    /* Dataframes */
    .stDataFrame {
        background-color: #1e293b;
        border-radius: 0.5rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 CyberProspect")
st.markdown("### Cybersecurity Sales Intelligence Platform")

st.markdown("""
Welcome to **CyberProspect**. This platform analyzes network exposure data to help cybersecurity sales teams identify and prioritize high-value prospects.

**How to use:**
1. 🏠 **Dashboard**: Executive overview of the entire dataset and market exposure.
2. 🔍 **Prospect Finder**: Filter and search for companies matching your Ideal Customer Profile.
3. 🏢 **Company Deep Dive**: Detailed breakdown of a single prospect's security posture.
4. 🌍 **Geo Map**: Visualize risk globally.
5. 🤖 **AI Pitch Generator**: Create hyper-personalized sales outreach emails based on actual vulnerabilities.

👈 *Select a page from the sidebar to get started.*
""")

# Setup initial database check
try:
    from utils.db import test_connection, init_db
    init_db() # Create views and tables
    if test_connection():
        st.success("✅ Connected to analytical database.")
        
        # Add a refresh button in the sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("Database Management")
        if st.sidebar.button("🔄 Rebuild Dashboard Cache"):
            with st.spinner("Rebuilding cache..."):
                init_db(force=True)
            st.success("Cache rebuilt!")
            st.rerun()
    else:
        st.warning("⚠️ Analytical database not initialized. Please run the ETL pipeline first.")
except Exception as e:
    st.error(f"Error checking database: {e}")

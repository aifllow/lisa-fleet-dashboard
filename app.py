"""
🚀 Lisa Fleet Dashboard - Starfleet Command
Design: Retro-Futuristic
Source: Google Sheets Data Bridge
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Page Config
st.set_page_config(
    page_title="LISA FLEET COMMAND",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Retro-Futuristic CSS
st.markdown(\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@400;600&family=JetBrains+Mono&display=swap');

.stApp {
    background: linear-gradient(180deg, #050a15 0%, #0a1226 100%);
    color: #e0e6ed;
}

/* Grid Overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(0, 212, 255, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 212, 255, 0.05) 1px, transparent 1px);
    background-size: 50px 50px;
    z-index: 0;
    pointer-events: none;
}

h1 {
    font-family: 'Orbitron', sans-serif;
    color: #00d4ff;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
    text-align: center;
    letter-spacing: 4px;
    padding: 2rem 0;
}

/* Metric Cards */
[data-testid=\"stMetric\"] {
    background: rgba(10, 20, 40, 0.8);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}

[data-testid=\"stMetricLabel\"] {
    color: #8b9bb4 !important;
    font-family: 'Exo 2', sans-serif;
    text-transform: uppercase;
}

[data-testid=\"stMetricValue\"] {
    color: #00d4ff !important;
    font-family: 'Orbitron', sans-serif;
}

/* Scanline Effect */
@keyframes scanline {
    0% { transform: translateY(-100vh); }
    100% { transform: translateY(100vh); }
}
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; height: 5px;
    background: rgba(0, 212, 255, 0.1);
    animation: scanline 10s linear infinite;
    z-index: 100;
    pointer-events: none;
}

/* Custom Status Card */
.agent-card {
    background: rgba(15, 25, 45, 0.9);
    border-left: 4px solid #00d4ff;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 4px;
}
</style>
\"\"\", unsafe_allow_html=True)

# Data Fetching
SHEET_URL = "https://docs.google.com/spreadsheets/d/1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4/export?format=csv"

def get_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # 假设第一行是我们要的数据
        return df.iloc[0]
    except Exception as e:
        st.error(f"Data Link Offline: {e}")
        return None

data = get_data()

if data is not None:
    st.markdown(\"<h1>◆ LISA FLEET COMMAND</h1>\", unsafe_allow_html=True)
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Agents Active", int(data.get('B', 0)))
    with col2:
        st.metric("Total Sessions", int(data.get('C', 0)))
    with col3:
        st.metric("Context Load", f"{data.get('E', 0)}%")
    with col4:
        st.metric("Gateway Status", str(data.get('F', 'UNKNOWN')))

    st.write("---")
    
    # Roster (Dummy for now, but linked to real counts)
    st.subheader("🛸 Fleet Roster")
    c1, c2, col3 = st.columns(3)
    
    agents = ["Lisa", "Chief Advisor", "Coder", "Researcher", "Writer", "Artist"]
    for i, name in enumerate(agents):
        with [c1, c2, col3][i % 3]:
            st.markdown(f\"\"\"
            <div class=\"agent-card\">
                <div style=\"color:#00d4ff; font-weight:bold;\">{name}</div>
                <div style=\"font-size:0.8rem; color:#8b9bb4;\">STATUS: ACTIVE</div>
            </div>
            \"\"\", unsafe_allow_html=True)

    st.write("---")
    st.caption(f"Last Sync: {data.get('A', 'N/A')} (CST)")
else:
    st.warning("📡 Waiting for Mac bridge signal...")

if st.button("Manual Refresh"):
    st.rerun()

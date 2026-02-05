"""
🚀 Lisa 舰队仪表板 - Streamlit MVP
设计风格: Retro-Futuristic (复古未来 - 星际舰队风)
差异化记忆点: 星际舰队指挥中心的感觉

技术栈: Streamlit + Google Sheets (数据源)
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import subprocess

# 页面配置
st.set_page_config(
    page_title="Lisa Fleet Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS - Retro-Futuristic 主题
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* 全局样式重置 */
.stApp {
    background: linear-gradient(180deg, #0a0f1a 0%, #0d1526 50%, #0a0f1a 100%);
    background-attachment: fixed;
}

/* 网格纹理 */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* 主容器 */
.main .block-container {
    padding-top: 2rem;
    max-width: 1400px;
}

/* 标题样式 */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    color: #00d4ff !important;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    letter-spacing: 2px;
}

h2, h3 {
    font-family: 'Exo 2', sans-serif !important;
    color: #8ecae6 !important;
}

/* 指标卡片 */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(13, 21, 38, 0.9) 0%, rgba(20, 30, 50, 0.9) 100%);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 
        0 4px 20px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

[data-testid="stMetricLabel"] {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6b7c93 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 28px !important;
    color: #00d4ff !important;
}

/* 状态卡片 */
.agent-card {
    background: linear-gradient(135deg, rgba(13, 21, 38, 0.95) 0%, rgba(20, 30, 50, 0.95) 100%);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s ease;
}

.agent-card:hover {
    border-color: rgba(0, 212, 255, 0.4);
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
}

.agent-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 16px;
    color: #00d4ff;
    margin-bottom: 8px;
}

.agent-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #8b9bb4;
}

.status-online { color: #00d67e; }
.status-offline { color: #ff4757; }
.status-busy { color: #ffa502; }

/* 配额条 */
.quota-bar {
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 10px;
}

.quota-fill {
    height: 100%;
    background: linear-gradient(90deg, #00d4ff 0%, #00d67e 100%);
    border-radius: 4px;
    transition: width 0.5s ease;
}

.quota-fill.warning {
    background: linear-gradient(90deg, #ffa502 0%, #ff6b35 100%);
}

.quota-fill.danger {
    background: linear-gradient(90deg, #ff4757 0%, #ff6b35 100%);
}

/* 侧边栏 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #0a0f1a 100%);
    border-right: 1px solid rgba(0, 212, 255, 0.1);
}

/* 扫描线动效 */
@keyframes scanline {
    0% { top: -10%; }
    100% { top: 110%; }
}

.stApp::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
    animation: scanline 8s linear infinite;
    pointer-events: none;
    z-index: 9999;
}

/* 隐藏 Streamlit 默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def load_fleet_status():
    """加载舰队状态数据"""
    agents_file = Path.home() / "clawd" / "fleet" / "agents.json"
    
    try:
        with open(agents_file) as f:
            data = json.load(f)
        return data.get("agents", {})
    except:
        return {}


def get_session_stats():
    """获取会话统计"""
    sessions_dir = Path.home() / ".clawdbot" / "agents" / "main" / "sessions"
    
    try:
        sessions = list(sessions_dir.glob("*.jsonl"))
        total_size = sum(s.stat().st_size for s in sessions) / (1024 * 1024)  # MB
        return {
            "count": len(sessions),
            "total_size_mb": round(total_size, 1)
        }
    except:
        return {"count": 0, "total_size_mb": 0}


def get_cron_jobs():
    """获取 Cron 任务"""
    try:
        result = subprocess.run(
            ["clawdbot", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except:
        return []


def main():
    # 标题
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 40px;">
        <h1 style="margin: 0; font-size: 32px;">◆ LISA FLEET COMMAND</h1>
        <p style="color: #6b7c93; font-family: 'JetBrains Mono', monospace; font-size: 12px; margin-top: 10px;">
            STARFLEET STATUS MONITOR • {timestamp}
        </p>
    </div>
    """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
    
    # 概览指标
    col1, col2, col3, col4 = st.columns(4)
    
    agents = load_fleet_status()
    sessions = get_session_stats()
    
    with col1:
        st.metric("AGENTS ONLINE", len(agents), "Active")
    
    with col2:
        st.metric("SESSIONS", sessions["count"], f"{sessions['total_size_mb']} MB")
    
    with col3:
        # 模拟配额数据
        st.metric("QUOTA USED", "45%", "-5%")
    
    with col4:
        st.metric("UPTIME", "99.9%", "+0.1%")
    
    st.markdown("<hr style='border: 1px solid rgba(0, 212, 255, 0.1); margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Agent 状态面板
    st.markdown("### 🛸 FLEET ROSTER")
    
    cols = st.columns(3)
    
    agent_configs = [
        ("Lisa", "Commander", "🚀", "online"),
        ("Chief Advisor", "Staff", "📋", "online"),
        ("Coder", "Executor", "🔧", "online"),
        ("Researcher", "Executor", "🔍", "online"),
        ("Writer", "Executor", "✍️", "online"),
        ("Artist", "Executor", "🎨", "online"),
    ]
    
    for i, (name, level, emoji, status) in enumerate(agent_configs):
        with cols[i % 3]:
            status_class = f"status-{status}"
            status_icon = "●" if status == "online" else "○"
            
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-name">{emoji} {name}</div>
                <div class="agent-status">
                    <span class="{status_class}">{status_icon}</span> {level}
                </div>
                <div class="quota-bar">
                    <div class="quota-fill" style="width: {60 + i * 5}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(0, 212, 255, 0.1); margin: 30px 0;'>", unsafe_allow_html=True)
    
    # 任务时间线
    st.markdown("### 📡 RECENT ACTIVITY")
    
    # 模拟活动数据
    activities = [
        {"time": "08:56", "agent": "Lisa", "action": "Generated trading report V5"},
        {"time": "08:49", "agent": "Lisa", "action": "Upgraded task system"},
        {"time": "08:37", "agent": "Lisa", "action": "Created frontend templates"},
        {"time": "07:30", "agent": "Lisa", "action": "Morning report sent"},
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div style="
            background: rgba(13, 21, 38, 0.8);
            border-left: 3px solid #00d4ff;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 0 8px 8px 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        ">
            <span style="color: #6b7c93;">{activity['time']}</span>
            <span style="color: #00d4ff; margin: 0 10px;">●</span>
            <span style="color: #8ecae6;">{activity['agent']}</span>
            <span style="color: #e8edf4; margin-left: 10px;">{activity['action']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # 页脚
    st.markdown("""
    <div style="
        text-align: center;
        padding: 40px 0 20px;
        color: #6b7c93;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
    ">
        ◆ Lisa Fleet Dashboard • MVP v1.0 • Retro-Futuristic Theme ◆
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

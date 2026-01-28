"""
🚢 Lisa 舰队指挥中心
Fleet Command Center Dashboard v2.0

部署：Streamlit Community Cloud
数据源：Google Sheets (Service Account 认证)
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="🚢 Lisa 舰队指挥中心",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS（响应式设计）
st.markdown("""
<style>
    /* 深色主题优化 */
    .stApp {
        background-color: #0e1117;
    }
    
    /* 卡片样式 - 响应式 */
    .agent-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #333;
        margin: 5px 0;
        min-height: 120px;
    }
    
    /* 状态指示灯 */
    .status-online { color: #00ff88; }
    .status-offline { color: #ff4444; }
    .status-idle { color: #888888; }
    .status-busy { color: #ffaa00; }
    
    /* 标题样式 - 响应式 */
    .main-title {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    /* 指标卡片 */
    .metric-card {
        background: #1a1f2e;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #333;
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ===== 响应式适配 ===== */
    
    /* 手机屏幕 (< 768px) */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.5rem !important;
        }
        
        .agent-card {
            padding: 12px;
            min-height: 100px;
        }
        
        .agent-card h3 {
            font-size: 1rem !important;
        }
        
        .agent-card p {
            font-size: 0.8rem !important;
        }
        
        /* Streamlit 列在手机上堆叠 */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* 指标卡片在手机上更紧凑 */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
    }
    
    /* 平板屏幕 (768px - 1024px) */
    @media (min-width: 768px) and (max-width: 1024px) {
        .main-title {
            font-size: 1.8rem !important;
        }
        
        /* 平板上显示 2 列 */
        [data-testid="column"] {
            min-width: 45% !important;
        }
    }
    
    /* 确保内容不溢出 */
    .stMarkdown, .stText {
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets 配置
SHEET_ID = "1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4"

# Agent 配置（emoji 和颜色）
AGENT_CONFIG = {
    'chief-advisor': {'emoji': '📋', 'color': '#4CAF50'},
    'resource-officer': {'emoji': '💰', 'color': '#FF9800'},
    'coder': {'emoji': '🔧', 'color': '#2196F3'},
    'researcher': {'emoji': '🔍', 'color': '#9C27B0'},
    'writer': {'emoji': '✍️', 'color': '#E91E63'},
    'artist': {'emoji': '🎨', 'color': '#00BCD4'},
    'translator': {'emoji': '🌐', 'color': '#FFEB3B'},
    'analyst': {'emoji': '📊', 'color': '#795548'},
    'general': {'emoji': '⚡', 'color': '#FF5722'},
}

# 密码保护
import os

def get_password():
    try:
        env_password = os.getenv('DASHBOARD_PASSWORD')
        if env_password:
            return env_password
        return st.secrets["dashboard"]["password"]
    except:
        return None

def check_password():
    def password_entered():
        if st.session_state["password"] == get_password():
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h1 class='main-title'>🔐 舰队指挥中心</h1>", unsafe_allow_html=True)
        st.text_input("请输入访问密码", type="password", on_change=password_entered, key="password")
        st.info("请联系舰长获取访问权限")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h1 class='main-title'>🔐 舰队指挥中心</h1>", unsafe_allow_html=True)
        st.text_input("请输入访问密码", type="password", on_change=password_entered, key="password")
        st.error("❌ 密码错误")
        return False
    return True

@st.cache_data(ttl=60)
def load_fleet_data():
    """从 Google Sheets 加载舰队状态数据"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
        )
        
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(SHEET_ID)
        worksheet = spreadsheet.sheet1
        
        all_values = worksheet.get_all_values()
        return all_values
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return None

def parse_fleet_data(raw_data):
    """解析舰队数据"""
    if not raw_data:
        return None, None, None
    
    # 解析系统状态（第1-2行）
    system_status = {
        'update_time': raw_data[1][0] if len(raw_data) > 1 else '',
        'default_model': raw_data[1][1] if len(raw_data) > 1 else '',
        'status': raw_data[1][2] if len(raw_data) > 1 else '',
        'fallback': raw_data[1][3] if len(raw_data) > 1 else '',
    }
    
    # 解析会话状态（第6-7行）
    session_info = {
        'session_count': raw_data[6][1] if len(raw_data) > 6 else '0',
        'active_sessions': raw_data[6][2] if len(raw_data) > 6 else '0',
        'total_tokens': raw_data[6][3] if len(raw_data) > 6 else '0',
    }
    
    # 解析 Agent 列表（第10行开始）
    agents = []
    for i in range(10, len(raw_data)):
        row = raw_data[i]
        if len(row) >= 6 and row[1]:  # 有 Agent ID
            agents.append({
                'update_time': row[0],
                'agent_id': row[1],
                'name': row[2],
                'role': row[3],
                'model': row[4],
                'status': row[5],
            })
    
    return system_status, session_info, agents

def render_status_badge(status):
    """渲染状态徽章"""
    status_map = {
        'Active': ('🟢', '在线', 'status-online'),
        'Ready': ('🟢', '就绪', 'status-online'),
        'Idle': ('⚪', '空闲', 'status-idle'),
        'Busy': ('🟡', '繁忙', 'status-busy'),
        'Offline': ('🔴', '离线', 'status-offline'),
        '✅': ('🟢', '正常', 'status-online'),
        '⏸️': ('⚪', '暂停', 'status-idle'),
        '❌': ('🔴', '异常', 'status-offline'),
    }
    
    for key, (icon, label, css_class) in status_map.items():
        if key in str(status):
            return icon, label, css_class
    return '⚪', '未知', 'status-idle'

def render_agent_card(agent):
    """渲染 Agent 卡片"""
    agent_id = agent['agent_id']
    config = AGENT_CONFIG.get(agent_id, {'emoji': '🤖', 'color': '#666'})
    icon, status_label, css_class = render_status_badge(agent['status'])
    
    # 简化模型名称
    model = agent['model']
    if 'claude' in model.lower():
        model_short = '☁️ Claude'
    elif 'gemini' in model.lower():
        model_short = '✨ Gemini'
    else:
        model_short = model[:15]
    
    st.markdown(f"""
    <div class="agent-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 2rem;">{config['emoji']}</span>
            <span class="{css_class}" style="font-size: 1.2rem;">{icon}</span>
        </div>
        <h3 style="margin: 10px 0 5px 0; color: #fff;">{agent['name']}</h3>
        <p style="margin: 0; color: #888; font-size: 0.9rem;">{agent['role']}</p>
        <p style="margin: 5px 0 0 0; color: #aaa; font-size: 0.8rem;">{model_short}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # 标题区域
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.markdown("<h1 class='main-title'>🚢 Lisa 舰队指挥中心</h1>", unsafe_allow_html=True)
        st.caption(f"最后刷新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col_refresh:
        st.write("")
        if st.button("🔄 刷新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # 加载数据
    raw_data = load_fleet_data()
    if not raw_data:
        st.error("无法加载数据")
        return
    
    system_status, session_info, agents = parse_fleet_data(raw_data)
    
    # ========== 顶部指标卡片 ==========
    st.subheader("📊 系统状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        online_count = len([a for a in agents if a['status'] in ['Ready', 'Active', '✅']])
        st.metric(
            label="🤖 Agent 在线",
            value=f"{online_count}/{len(agents)}",
            delta="正常" if online_count == len(agents) else f"{len(agents)-online_count} 离线"
        )
    
    with col2:
        status_icon = "🟢" if system_status['status'] == 'Active' else "🔴"
        st.metric(
            label="☁️ Claude OAuth",
            value=status_icon + " 有效" if 'Active' in system_status['status'] else "❌ 检查",
        )
    
    with col3:
        st.metric(
            label="📊 活跃会话",
            value=session_info['active_sessions'],
        )
    
    with col4:
        tokens = int(session_info['total_tokens']) if session_info['total_tokens'].isdigit() else 0
        st.metric(
            label="🎯 总 Tokens",
            value=f"{tokens:,}",
        )
    
    st.divider()
    
    # ========== Agent 舰队 ==========
    st.subheader("👥 Agent 舰队")
    
    # 3列网格布局
    cols = st.columns(3)
    for idx, agent in enumerate(agents):
        with cols[idx % 3]:
            render_agent_card(agent)
    
    st.divider()
    
    # ========== 底部信息 ==========
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("**🔗 快速链接**")
        st.markdown("- [Google Sheets 数据源](https://docs.google.com/spreadsheets/d/1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4)")
        st.markdown("- [GitHub 仓库](https://github.com/aifllow/lisa-fleet-dashboard)")
    
    with col_info2:
        st.markdown("**ℹ️ 系统信息**")
        st.markdown(f"- 默认模型: `{system_status['default_model'][:30]}...`")
        st.markdown(f"- 数据更新: {system_status['update_time']}")
    
    st.divider()
    col_footer1, col_footer2 = st.columns([3, 1])
    with col_footer1:
        st.caption("🚢 Lisa 舰队 | 舰长: Neal | 总指挥官: Lisa")
    with col_footer2:
        st.markdown("[📱 移动版](./📱_Mobile)", unsafe_allow_html=True)

# 运行
if check_password():
    main()

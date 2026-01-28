"""
📱 Lisa 舰队指挥中心 - 移动端
Mobile-optimized Fleet Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# 页面配置 - 移动优化
st.set_page_config(
    page_title="📱 舰队状态",
    page_icon="🚢",
    layout="centered",  # 居中布局更适合手机
    initial_sidebar_state="collapsed"
)

# 移动端专用 CSS
st.markdown("""
<style>
    /* 隐藏侧边栏 */
    [data-testid="stSidebar"] { display: none; }
    
    /* 大号状态卡片 */
    .mobile-status-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        text-align: center;
        border: 2px solid #333;
    }
    
    .mobile-status-card.success { border-color: #00ff88; }
    .mobile-status-card.warning { border-color: #ffaa00; }
    .mobile-status-card.error { border-color: #ff4444; }
    
    /* 大号数字 */
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .big-number.green { color: #00ff88; }
    .big-number.yellow { color: #ffaa00; }
    .big-number.red { color: #ff4444; }
    
    /* 状态标签 */
    .status-label {
        font-size: 1rem;
        color: #888;
    }
    
    /* Agent 列表项 */
    .agent-list-item {
        background: #1a1f2e;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 移动端标题 */
    .mobile-title {
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets 配置
SHEET_ID = "1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4"

# 密码保护（复用主页逻辑）
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
        if st.session_state.get("mobile_password") == get_password():
            st.session_state["mobile_auth"] = True
        else:
            st.session_state["mobile_auth"] = False

    if not st.session_state.get("mobile_auth"):
        st.markdown("<h2 style='text-align:center;'>🔐 舰队指挥中心</h2>", unsafe_allow_html=True)
        st.text_input("访问密码", type="password", key="mobile_password", on_change=password_entered)
        if st.session_state.get("mobile_auth") == False:
            st.error("密码错误")
        return False
    return True

@st.cache_data(ttl=60)
def load_fleet_data():
    """加载舰队数据"""
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
        return worksheet.get_all_values()
    except Exception as e:
        return None

def parse_agents(raw_data):
    """解析 Agent 数据"""
    agents = []
    for i in range(10, len(raw_data)):
        row = raw_data[i]
        if len(row) >= 6 and row[1]:
            agents.append({
                'id': row[1],
                'name': row[2],
                'role': row[3],
                'status': row[5],
            })
    return agents

def main():
    # 标题 + 刷新
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("## 🚢 舰队状态")
    with col2:
        if st.button("🔄"):
            st.cache_data.clear()
            st.rerun()
    
    st.caption(f"更新: {datetime.now().strftime('%H:%M')}")
    
    # 加载数据
    raw_data = load_fleet_data()
    if not raw_data:
        st.error("无法加载数据")
        return
    
    agents = parse_agents(raw_data)
    
    # ===== 核心指标（大卡片）=====
    online = len([a for a in agents if a['status'] in ['Ready', 'Active', '✅']])
    total = len(agents)
    offline = total - online
    
    # 主状态卡片
    if offline == 0:
        card_class = "success"
        status_text = "✅ 全部在线"
        number_class = "green"
    elif offline <= 2:
        card_class = "warning"
        status_text = f"⚠️ {offline} 个离线"
        number_class = "yellow"
    else:
        card_class = "error"
        status_text = f"❌ {offline} 个离线"
        number_class = "red"
    
    st.markdown(f"""
    <div class="mobile-status-card {card_class}">
        <div class="status-label">Agent 在线</div>
        <div class="big-number {number_class}">{online}/{total}</div>
        <div>{status_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 系统状态
    system_status = raw_data[1][2] if len(raw_data) > 1 else ''
    oauth_ok = 'Active' in system_status
    
    st.markdown(f"""
    <div class="mobile-status-card {'success' if oauth_ok else 'error'}">
        <div class="status-label">Claude OAuth</div>
        <div class="big-number {'green' if oauth_ok else 'red'}">{'✓' if oauth_ok else '✗'}</div>
        <div>{'有效' if oauth_ok else '需要重新认证'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== Agent 列表（可展开）=====
    st.markdown("---")
    st.markdown("### 👥 Agent 详情")
    
    for agent in agents:
        status = agent['status']
        if status in ['Ready', 'Active', '✅']:
            icon = "🟢"
        elif status in ['⏸️', 'Idle']:
            icon = "⚪"
        else:
            icon = "🔴"
        
        with st.expander(f"{icon} {agent['name']} - {agent['role']}"):
            st.write(f"**状态**: {status}")
            st.write(f"**ID**: `{agent['id']}`")
    
    # 底部
    st.markdown("---")
    st.caption("🚢 Lisa 舰队 | [桌面版](./)")

# 运行
if check_password():
    main()

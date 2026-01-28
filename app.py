"""
🚢 Lisa 舰队指挥中心
Fleet Command Center Dashboard v3.0

自动适配桌面/移动端
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

# 响应式 CSS - 桌面/移动自动切换
st.markdown("""
<style>
    /* ===== 通用样式 ===== */
    .stApp { background-color: #0e1117; }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* 标题 */
    .main-title {
        font-size: 1.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Agent 卡片 */
    .agent-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #333;
        margin: 6px 0;
    }
    
    /* 移动端大卡片 */
    .mobile-big-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        text-align: center;
        border: 2px solid #333;
    }
    .mobile-big-card.ok { border-color: #00ff88; }
    .mobile-big-card.warn { border-color: #ffaa00; }
    .mobile-big-card.bad { border-color: #ff4444; }
    
    .big-num { font-size: 2.5rem; font-weight: bold; margin: 8px 0; }
    .big-num.green { color: #00ff88; }
    .big-num.red { color: #ff4444; }
    
    /* ===== 桌面端显示，移动端隐藏 ===== */
    .desktop-only { display: block; }
    
    /* ===== 移动端显示，桌面端隐藏 ===== */
    .mobile-only { display: none; }
    
    /* ===== 响应式断点 ===== */
    @media (max-width: 768px) {
        .desktop-only { display: none !important; }
        .mobile-only { display: block !important; }
        
        .main-title { font-size: 1.4rem; }
        
        /* 移动端列堆叠 */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        
        /* 紧凑指标 */
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets 配置
SHEET_ID = "1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4"

# Agent 配置
AGENT_EMOJI = {
    'chief-advisor': '📋', 'resource-officer': '💰', 'coder': '🔧',
    'researcher': '🔍', 'writer': '✍️', 'artist': '🎨',
    'translator': '🌐', 'analyst': '📊', 'general': '⚡',
}

# 密码保护
import os

def check_password():
    def get_pw():
        try:
            return os.getenv('DASHBOARD_PASSWORD') or st.secrets["dashboard"]["password"]
        except:
            return None
    
    def on_submit():
        if st.session_state.get("pw_input") == get_pw():
            st.session_state["authed"] = True
        else:
            st.session_state["authed"] = False

    if not st.session_state.get("authed"):
        st.markdown("<h2 style='text-align:center'>🔐 舰队指挥中心</h2>", unsafe_allow_html=True)
        st.text_input("访问密码", type="password", key="pw_input", on_change=on_submit)
        if st.session_state.get("authed") == False:
            st.error("密码错误")
        return False
    return True

@st.cache_data(ttl=60)
def load_data():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly",
                    "https://www.googleapis.com/auth/drive.readonly"]
        )
        gc = gspread.authorize(creds)
        return gc.open_by_key(SHEET_ID).sheet1.get_all_values()
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

def parse_data(raw):
    if not raw or len(raw) < 11:
        return {}, []
    
    system = {
        'status': raw[1][2] if len(raw[1]) > 2 else '',
        'model': raw[1][1] if len(raw[1]) > 1 else '',
        'sessions': raw[6][2] if len(raw) > 6 and len(raw[6]) > 2 else '0',
        'tokens': raw[6][3] if len(raw) > 6 and len(raw[6]) > 3 else '0',
    }
    
    agents = []
    for row in raw[10:]:
        if len(row) >= 6 and row[1]:
            agents.append({
                'id': row[1], 'name': row[2], 'role': row[3],
                'model': row[4], 'status': row[5]
            })
    return system, agents

def main():
    raw = load_data()
    if not raw:
        return
    
    system, agents = parse_data(raw)
    online = len([a for a in agents if a['status'] in ['Ready', 'Active', '✅']])
    total = len(agents)
    oauth_ok = 'Active' in system.get('status', '')
    
    # ========== 头部 ==========
    col_t, col_r = st.columns([5, 1])
    with col_t:
        st.markdown("<h1 class='main-title'>🚢 Lisa 舰队指挥中心</h1>", unsafe_allow_html=True)
    with col_r:
        if st.button("🔄 刷新"):
            st.cache_data.clear()
            st.rerun()
    
    st.caption(f"更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.divider()
    
    # ========== 移动端视图 ==========
    st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
    
    # 大卡片 - Agent 状态
    card_class = "ok" if online == total else ("warn" if online >= total - 2 else "bad")
    num_class = "green" if online == total else "red"
    st.markdown(f"""
    <div class="mobile-big-card {card_class}">
        <div style="color:#888">Agent 在线</div>
        <div class="big-num {num_class}">{online}/{total}</div>
        <div>{'✅ 全部正常' if online == total else f'⚠️ {total-online} 个离线'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 大卡片 - OAuth
    st.markdown(f"""
    <div class="mobile-big-card {'ok' if oauth_ok else 'bad'}">
        <div style="color:#888">Claude OAuth</div>
        <div class="big-num {'green' if oauth_ok else 'red'}">{'✓' if oauth_ok else '✗'}</div>
        <div>{'有效' if oauth_ok else '需要认证'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent 列表
    st.markdown("#### 👥 Agent 详情")
    for a in agents:
        icon = "🟢" if a['status'] in ['Ready', 'Active', '✅'] else "⚪"
        with st.expander(f"{icon} {a['name']} - {a['role']}"):
            st.write(f"状态: {a['status']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 桌面端视图 ==========
    st.markdown('<div class="desktop-only">', unsafe_allow_html=True)
    
    # 指标行
    st.subheader("📊 系统状态")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🤖 Agent", f"{online}/{total}", "正常" if online == total else f"{total-online} 离线")
    c2.metric("☁️ Claude", "✅ 有效" if oauth_ok else "❌ 过期")
    c3.metric("📊 会话", system.get('sessions', '0'))
    tokens = system.get('tokens', '0')
    c4.metric("🎯 Tokens", f"{int(tokens):,}" if tokens.isdigit() else tokens)
    
    st.divider()
    
    # Agent 网格
    st.subheader("👥 Agent 舰队")
    cols = st.columns(3)
    for i, a in enumerate(agents):
        with cols[i % 3]:
            emoji = AGENT_EMOJI.get(a['id'], '🤖')
            status_icon = "🟢" if a['status'] in ['Ready', 'Active', '✅'] else "⚪"
            model_short = "☁️ Claude" if 'claude' in a['model'].lower() else "✨ Gemini"
            st.markdown(f"""
            <div class="agent-card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:1.8rem">{emoji}</span>
                    <span style="font-size:1.2rem">{status_icon}</span>
                </div>
                <h4 style="margin:8px 0 4px 0;color:#fff">{a['name']}</h4>
                <p style="margin:0;color:#888;font-size:0.85rem">{a['role']}</p>
                <p style="margin:4px 0 0 0;color:#aaa;font-size:0.8rem">{model_short}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部
    st.divider()
    st.caption("🚢 Lisa 舰队 | 舰长: Neal | 总指挥官: Lisa")

if check_password():
    main()

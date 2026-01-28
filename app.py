"""
🚢 Lisa 舰队指挥中心
Fleet Command Center Dashboard v4.0

单一响应式设计
"""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="🚢 Lisa 舰队",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 简洁响应式 CSS
st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebar"] { display: none; }
    
    .status-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #333;
    }
    .status-card.ok { border-left-color: #22c55e; }
    .status-card.warn { border-left-color: #eab308; }
    .status-card.bad { border-left-color: #ef4444; }
    
    .big-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .big-value.green { color: #22c55e; }
    .big-value.yellow { color: #eab308; }
    .big-value.red { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

SHEET_ID = "1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4"

import os

def check_password():
    def get_pw():
        try:
            return os.getenv('DASHBOARD_PASSWORD') or st.secrets["dashboard"]["password"]
        except:
            return None
    
    if "authed" not in st.session_state:
        st.session_state.authed = False
    
    if not st.session_state.authed:
        st.title("🔐 舰队指挥中心")
        pw = st.text_input("访问密码", type="password")
        if st.button("进入"):
            if pw == get_pw():
                st.session_state.authed = True
                st.rerun()
            else:
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
        return None

def main():
    # 标题
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🚢 舰队状态")
    with col2:
        if st.button("🔄"):
            st.cache_data.clear()
            st.rerun()
    
    st.caption(f"更新: {datetime.now().strftime('%H:%M:%S')}")
    
    # 加载数据
    raw = load_data()
    if not raw:
        st.error("数据加载失败")
        return
    
    # 解析
    system_status = raw[1][2] if len(raw) > 1 and len(raw[1]) > 2 else ''
    oauth_ok = 'Active' in system_status
    
    agents = []
    for row in raw[10:]:
        if len(row) >= 6 and row[1]:
            agents.append({
                'name': row[2],
                'role': row[3],
                'status': row[5]
            })
    
    online = len([a for a in agents if a['status'] in ['Ready', 'Active', '✅']])
    total = len(agents)
    
    # ===== 状态卡片 =====
    
    # Agent 状态
    if online == total:
        card_class, val_class, status_text = "ok", "green", "全部正常"
    elif online >= total - 2:
        card_class, val_class, status_text = "warn", "yellow", f"{total-online} 个离线"
    else:
        card_class, val_class, status_text = "bad", "red", f"{total-online} 个离线"
    
    st.markdown(f"""
    <div class="status-card {card_class}">
        <div style="color:#94a3b8;font-size:0.9rem">🤖 Agent 在线</div>
        <div class="big-value {val_class}">{online} / {total}</div>
        <div style="color:#64748b">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # OAuth 状态
    st.markdown(f"""
    <div class="status-card {'ok' if oauth_ok else 'bad'}">
        <div style="color:#94a3b8;font-size:0.9rem">☁️ Claude OAuth</div>
        <div class="big-value {'green' if oauth_ok else 'red'}">{'✓ 有效' if oauth_ok else '✗ 过期'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== Agent 列表 =====
    st.markdown("---")
    st.subheader("👥 Agent 列表")
    
    for a in agents:
        ok = a['status'] in ['Ready', 'Active', '✅']
        icon = "🟢" if ok else "⚪"
        with st.expander(f"{icon} {a['name']} ({a['role']})"):
            st.write(f"**状态**: {a['status']}")
    
    # 底部
    st.markdown("---")
    st.caption("🚢 Lisa 舰队 | 舰长: Neal")

if check_password():
    main()

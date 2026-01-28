"""
🚢 Lisa 舰队指挥中心
Fleet Command Center Dashboard

部署：Streamlit Community Cloud
数据源：Google Sheets (Service Account 认证)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json

# 页面配置
st.set_page_config(
    page_title="🚢 Lisa 舰队指挥中心",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Sheets 配置
SHEET_ID = "1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4"

# 密码保护
import os
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_password():
    """获取密码：优先环境变量，降级到 secrets.toml"""
    try:
        env_password = os.getenv('DASHBOARD_PASSWORD')
        if env_password:
            return env_password
        return st.secrets["dashboard"]["password"]
    except Exception as e:
        logging.error(f"密码配置错误: {e}")
        return None

def check_password():
    """安全的密码验证"""
    def password_entered():
        try:
            correct_password = get_password()
            if correct_password is None:
                st.session_state["password_correct"] = False
                return
            if st.session_state["password"] == correct_password:
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False
        except Exception as e:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 舰队指挥中心")
        st.text_input("请输入访问密码", type="password", on_change=password_entered, key="password")
        st.info("请联系舰长获取访问权限")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 舰队指挥中心")
        st.text_input("请输入访问密码", type="password", on_change=password_entered, key="password")
        st.error("❌ 密码错误")
        return False
    else:
        return True

# 使用 Service Account 加载数据
@st.cache_data(ttl=60)
def load_fleet_data():
    """从 Google Sheets 加载舰队状态数据（Service Account 认证）"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # 从 Streamlit secrets 获取服务账号凭据
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
        
        # 获取所有数据
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return None

# 主界面
def main():
    st.title("🚢 Lisa 舰队指挥中心")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    df = load_fleet_data()
    
    if df is not None and not df.empty:
        st.subheader("📊 系统状态")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(df)
        active = len(df[df['状态'].str.contains('✅|🟢', na=False)]) if '状态' in df.columns else 0
        warning = len(df[df['状态'].str.contains('⚠️|🟡', na=False)]) if '状态' in df.columns else 0
        error = len(df[df['状态'].str.contains('❌|🔴', na=False)]) if '状态' in df.columns else 0
        
        col1.metric("总组件", total)
        col2.metric("正常运行", active)
        col3.metric("需要注意", warning)
        col4.metric("异常", error, delta=None if error == 0 else f"-{error}")
        
        st.divider()
        
        st.subheader("👥 Agent 舰队")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        with st.expander("📋 查看原始数据"):
            st.write(df.to_dict())
    else:
        st.warning("⚠️ 暂无数据，请检查 Google Sheets 连接")
        st.info("如果持续出现此问题，请确认服务账号已被添加为 Sheet 的查看者")
    
    st.divider()
    st.caption("🚢 Lisa 舰队 | 舰长: Neal | 总指挥官: Lisa")
    st.caption("探索、执行、进化 — Explore, Execute, Evolve")

if check_password():
    main()

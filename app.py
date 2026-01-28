"""
🚢 Lisa 舰队指挥中心
Fleet Command Center Dashboard

部署：Streamlit Community Cloud
数据源：Google Sheets
"""

import streamlit as st
import pandas as pd
import requests
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
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# 密码保护（安全加固版 v2.1）
import os
import logging

# 配置服务端日志（不暴露给用户）
logging.basicConfig(
    filename='.streamlit/dashboard.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_password():
    """获取密码：优先环境变量，降级到 secrets.toml"""
    try:
        # 优先使用环境变量（便于容器化部署）
        env_password = os.getenv('DASHBOARD_PASSWORD')
        if env_password:
            return env_password
        # 降级到 secrets.toml
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
                logging.error("无法获取密码配置")
                return
            if st.session_state["password"] == correct_password:
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False
                logging.warning("密码验证失败")
        except Exception as e:
            st.session_state["password_correct"] = False
            logging.error(f"密码验证异常: {e}")

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

# 加载数据
@st.cache_data(ttl=60)
def load_fleet_data():
    """从 Google Sheets 加载舰队状态数据"""
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return None

# 主界面
def main():
    # 标题
    st.title("🚢 Lisa 舰队指挥中心")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 刷新按钮
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # 加载数据
    df = load_fleet_data()
    
    if df is not None and not df.empty:
        # 系统状态概览
        st.subheader("📊 系统状态")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # 统计状态
        total = len(df)
        active = len(df[df['状态'].str.contains('✅|🟢', na=False)]) if '状态' in df.columns else 0
        warning = len(df[df['状态'].str.contains('⚠️|🟡', na=False)]) if '状态' in df.columns else 0
        error = len(df[df['状态'].str.contains('❌|🔴', na=False)]) if '状态' in df.columns else 0
        
        col1.metric("总组件", total)
        col2.metric("正常运行", active, delta=None)
        col3.metric("需要注意", warning, delta=None)
        col4.metric("异常", error, delta=None if error == 0 else f"-{error}")
        
        st.divider()
        
        # Agent 舰队
        st.subheader("👥 Agent 舰队")
        
        # 显示数据表格
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )
        
        st.divider()
        
        # 详细信息
        with st.expander("📋 查看原始数据"):
            st.write(df.to_dict())
    else:
        st.warning("⚠️ 暂无数据，请检查 Google Sheets 连接")
        st.info(f"数据源: {SHEET_URL}")
    
    # 底部信息
    st.divider()
    st.caption("🚢 Lisa 舰队 | 舰长: Neal | 总指挥官: Lisa")
    st.caption("探索、执行、进化 — Explore, Execute, Evolve")

# 运行
if check_password():
    main()

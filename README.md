# 🚢 Lisa 舰队指挥中心

实时舰队状态仪表板

## 部署到 Streamlit Cloud

### 步骤 1: 推送到 GitHub
```bash
cd ~/clawd
git add fleet/streamlit-dashboard
git commit -m "Add Streamlit dashboard"
git push origin main
```

### 步骤 2: 连接 Streamlit Cloud
1. 访问 https://share.streamlit.io
2. 登录 GitHub 账号
3. 选择仓库: `aifllow/clawd` (或你的仓库名)
4. 选择文件: `fleet/streamlit-dashboard/app.py`
5. 点击 Deploy

### 步骤 3: 配置 Secrets
在 Streamlit Cloud 设置中添加:
```toml
password = "your_secure_password"
```

### 本地测试
```bash
cd fleet/streamlit-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## 数据源

- Google Sheets: https://docs.google.com/spreadsheets/d/1A8bYu9VoTeuukLUZ17CC2EpPSgntVOe1nNr5WdPfvW4/edit

## 功能

- ✅ 密码保护
- ✅ 实时状态显示
- ✅ Agent 舰队概览
- ✅ 自动刷新（60秒缓存）
- ✅ 响应式设计

---

*舰队格言: 探索、执行、进化*

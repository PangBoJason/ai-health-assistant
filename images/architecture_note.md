# 架构图说明

## 系统架构图
用户提供的架构图显示了一个完整的AI健康助手系统架构：

### 前端层 (Streamlit Frontend)
- Dashboard (仪表板)
- Chat UI (聊天界面) 
- Goals (目标管理)
- Profile (用户配置)

### AI代理层 (AI Agents)
- Fitness Agent (健身代理)
- Nutrition Agent (营养代理)
- Wellness Agent (健康代理)
- Supervisor Agent (监督代理)

### AI核心 (OpenAI GPT-4o)
- 处理所有AI推理和对话生成

### 业务逻辑层 (Business Logic)
- Visualization (可视化)
- Goals Management (目标管理)
- Data Processing (数据处理)
- Analytics (分析)

### 技术栈
- Frontend: Streamlit, Plotly, CSS
- AI: LangChain, LangGraph, OpenAI GPT-4o
- Backend: Python, SQLAlchemy, Pandas
- Database: SQLite

**注意**: 请将用户提供的架构图保存为 `architecture.png` 文件，放在此 images 文件夹中。

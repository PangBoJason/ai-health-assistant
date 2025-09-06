# 智能健康助手 🏥🤖

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://python.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个融合AI健身教练和健康监督功能的综合健康管理助手，基于多代理系统架构。

## ✨ 功能特性

### 🏋️ 健身教练模块
- 个性化运动计划制定
- 根据目标和身体状况调整
- 支持减重、增肌、耐力等多种目标
- 安全性指导和注意事项
- **SMART目标管理**: 具体、可测量的健身目标设定

### 🍎 营养师模块
- 个性化饮食计划
- 营养原则指导
- 考虑饮食偏好和限制
- 每日餐食建议
- **营养跟踪**: 卡路里和营养素摄入记录

### 🧘 心理健康顾问模块
- 压力管理技巧
- 冥想和放松指导
- 心理健康建议
- 生活方式优化
- **情绪跟踪**: 每日心情和压力水平记录

### 📊 数据可视化模块
- **健康趋势分析**: 体重、运动频率、心情变化图表
- **进度跟踪**: 目标完成情况可视化
- **统计报告**: 周/月健康数据汇总
- **交互式图表**: 基于Plotly的动态数据展示

### 🎯 目标管理模块
- **SMART目标设定**: 具体、可测量、可达成的目标
- **进度跟踪**: 实时目标完成情况
- **成就系统**: 目标达成奖励和激励
- **目标模板**: 预设的常见健康目标

## 🛠️ 技术架构

![系统架构图](https://github.com/PangBoJason/ai-health-assistant/blob/main/images/baselinepicture.png)

### 技术栈
- **前端**: Streamlit + Plotly + CSS
- **AI框架**: LangChain + LangGraph + OpenAI GPT-4o
- **后端**: Python + SQLAlchemy + Pandas
- **数据库**: SQLite

### 系统组件
- **多代理系统**: 健身助手、营养师、心理健康顾问、监督代理
- **业务逻辑**: 数据可视化、目标管理、数据处理、分析模块
- **用户界面**: 仪表板、聊天界面、目标管理、用户配置
- **数据持久化**: 用户配置、健康记录、目标跟踪

## 📦 安装步骤

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd smart-health-assistant
```

### 2. 创建虚拟环境
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
编辑 `.env` 文件，确保包含：
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.chatanywhere.org/v1
```

### 5. 验证安装
```bash
# 验证依赖是否正确安装
python -c "import streamlit, langchain, langchain_openai; print('✅ 所有依赖安装成功！')"
```

### 6. 运行应用
```bash
streamlit run main.py
```

应用将在浏览器中自动打开 `http://localhost:8501`

## 🎯 使用方法

### 智能对话模式
1. 选择"智能对话"模式
2. 直接与助手对话，询问健康相关问题
3. 系统会自动路由到合适的专业助手

### 快速规划模式
1. 选择"快速规划"模式
2. 填写相关表单信息
3. 获得结构化的健康计划

## 💡 使用示例

### 健身咨询
```
用户：我想减重，每周可以锻炼3次，每次45分钟，应该怎么安排？
助手：🏋️ 健身教练会为您制定减重专项计划...
```

### 营养咨询
```
用户：我想增肌，应该怎么安排饮食？
助手：🍎 营养师会为您提供增肌营养策略...
```

### 心理健康
```
用户：最近工作压力很大，有什么缓解方法吗？
助手：🧘 心理健康顾问会为您提供压力管理技巧...
```

## 🔧 自定义配置

### 添加外部API
如果您有健身和营养API密钥，可以在 `.env` 文件中添加：
```
EXERCISE_API_KEY=your_exercise_api_key
DIET_API_KEY=your_diet_api_key
```

### 模型配置
可以在 `agents.py` 中修改模型配置：
```python
llm = ChatOpenAI(
    model="gpt-4o",  # 可改为其他模型
    temperature=0.7  # 调整创造性
)
```

## 📁 项目结构

```
smart-health-assistant/
├── main.py                    # 🚀 主应用入口 (Streamlit多页面应用)
├── agents.py                  # 🤖 多代理系统 (健身/营养/心理健康助手)
├── tools.py                   # 🛠️ 工具函数和数据处理
├── core/
│   └── database.py            # 💾 数据持久化 (SQLAlchemy + SQLite)
├── modules/
│   ├── visualization.py       # 📊 数据可视化 (Plotly图表)
│   ├── dashboard.py           # 📋 仪表板界面
│   └── goals.py              # 🎯 目标管理系统
├── images/                    # 🖼️ 文档图片资源
│   └── architecture.png       # 系统架构图
├── requirements.txt           # 📦 依赖包清单
├── .env                       # 🔐 环境变量配置
├── .gitignore                # 🚫 Git忽略文件
└── README.md                 # 📖 项目说明文档
```

### 核心模块说明

- **`main.py`**: Streamlit多页面应用的主入口，集成所有功能模块
- **`agents.py`**: 基于LangGraph的多代理系统，包含专业健康助手
- **`core/database.py`**: 完整的数据持久化解决方案，支持用户配置、健康记录、目标跟踪
- **`modules/visualization.py`**: 基于Plotly的交互式数据可视化
- **`modules/dashboard.py`**: 健康数据概览和快速操作界面
- **`modules/goals.py`**: SMART目标管理系统，支持目标设定、跟踪和成就

## ⚠️ 注意事项

1. **免责声明**: 本助手仅提供建议，不能替代专业医疗咨询
2. **API成本**: 使用GPT-4o会产生API调用费用
3. **数据隐私**: 用户数据仅在会话期间保存，不会永久存储

## 🚀 未来计划

- [ ] 添加数据持久化
- [ ] 集成更多外部健康API
- [ ] 添加用户账户系统
- [ ] 支持多语言
- [ ] 移动端适配
- [ ] 社交功能

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License

## 🔗 相关链接

- [LangChain文档](https://python.langchain.com/)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [Streamlit文档](https://docs.streamlit.io/)
- [ChatAnywhere API](https://api.chatanywhere.org/)

---

如有问题，请联系项目维护者或提交Issue。

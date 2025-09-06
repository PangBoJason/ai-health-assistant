# 智能健康助手

一个融合AI健身教练和健康监督功能的综合健康管理助手，基于多代理系统架构。

## ✨ 功能特性

### 🏋️ 健身教练
- 个性化运动计划制定
- 根据目标和身体状况调整
- 支持减重、增肌、耐力等多种目标
- 安全性指导和注意事项

### 🍎 营养师
- 个性化饮食计划
- 营养原则指导
- 考虑饮食偏好和限制
- 每日餐食建议

### 🧘 心理健康顾问
- 压力管理技巧
- 冥想和放松指导
- 心理健康建议
- 生活方式优化

## 🛠️ 技术架构

- **框架**: LangGraph + LangChain
- **AI模型**: GPT-4o (通过ChatAnywhere API)
- **前端**: Streamlit
- **语言**: Python 3.8+

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

### 5. 运行应用
```bash
streamlit run main.py
```

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
├── main.py              # 主应用入口
├── agents.py            # 多代理系统
├── tools.py             # 工具函数和数据
├── requirements.txt     # 依赖包
├── .env                 # 环境变量
└── README.md           # 项目说明
```

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

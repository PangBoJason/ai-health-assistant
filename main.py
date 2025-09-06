"""
智能健康助手 - 主应用文件
融合多代理系统、数据持久化、可视化和目标管理
"""
import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# 导入核心模块
from core.database import DatabaseManager
from modules.visualization import HealthVisualizer
from modules.dashboard import Dashboard
from modules.goals import GoalManager
from agents import HealthAssistant

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="智能健康助手",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f0f2f6, #ffffff);
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """初始化应用"""
    # 初始化数据库
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    
    # 初始化可视化工具
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = HealthVisualizer()
    
    # 初始化仪表板
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = Dashboard(st.session_state.db, st.session_state.visualizer)
    
    # 初始化目标管理器
    if 'goal_manager' not in st.session_state:
        st.session_state.goal_manager = GoalManager(st.session_state.db, st.session_state.visualizer)
    
    # 初始化健康助手
    if 'health_assistant' not in st.session_state:
        st.session_state.health_assistant = HealthAssistant()
    
    # 初始化页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 🏥 智能健康助手")
        st.markdown("---")
        
        # 导航菜单
        pages = {
            "🏠 仪表板": "dashboard",
            "💬 AI助手": "ai_chat", 
            "🎯 目标管理": "goals",
            "👤 个人档案": "profile",
            "📊 数据分析": "analytics",
            "⚙️ 设置": "settings"
        }
        
        for page_name, page_key in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # 今日激励
        st.markdown("### 💡 今日激励")
        motivation = st.session_state.goal_manager.get_motivation_message()
        st.info(motivation)
        
        # 快速统计
        st.markdown("### 📈 快速统计")
        stats = st.session_state.db.get_dashboard_stats()
        
        if stats.get('current_weight', 0) > 0:
            st.metric("当前体重", f"{stats['current_weight']:.1f} kg")
        
        st.metric("本周运动", f"{stats.get('week_exercises', 0)} 次")
        st.metric("活跃目标", f"{stats.get('active_goals', 0)} 个")

def render_dashboard_page():
    """渲染仪表板页面"""
    st.session_state.dashboard.render_dashboard()

def render_ai_chat_page():
    """渲染AI助手页面"""
    st.title("💬 AI健康助手")
    st.markdown("与我聊聊你的健康问题，我会为你提供专业建议！")
    
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是你的AI健康助手。我可以帮你制定健身计划、营养建议和心理健康指导。有什么可以帮助你的吗？"}
        ]
    
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 聊天输入
    if prompt := st.chat_input("请输入你的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成AI回复
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    # 调用健康助手
                    response = st.session_state.health_assistant.process_message(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"抱歉，我暂时无法回答。错误信息：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def render_goals_page():
    """渲染目标管理页面"""
    st.session_state.goal_manager.render_goal_management_page()

def render_profile_page():
    """渲染个人档案页面"""
    st.title("👤 个人档案管理")
    
    # 获取用户档案
    user_profile = st.session_state.db.get_user_profile()
    
    if user_profile:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("基本信息")
            with st.form("profile_form"):
                name = st.text_input("姓名", value=user_profile.name or "")
                age = st.number_input("年龄", min_value=1, max_value=120, value=user_profile.age or 25)
                gender = st.selectbox("性别", ["男", "女", "其他"], 
                                    index=["男", "女", "其他"].index(user_profile.gender) if user_profile.gender in ["男", "女", "其他"] else 0)
                height = st.number_input("身高 (cm)", min_value=100.0, max_value=250.0, value=user_profile.height or 170.0)
                weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=user_profile.weight or 65.0)
                
                if st.form_submit_button("更新基本信息"):
                    profile_data = {
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'height': height,
                        'weight': weight
                    }
                    if st.session_state.db.update_user_profile(profile_data):
                        st.success("个人信息更新成功！")
                        st.rerun()
                    else:
                        st.error("更新失败，请重试")
        
        with col2:
            st.subheader("健康偏好")
            with st.form("preferences_form"):
                activity_level = st.selectbox("活动水平", 
                    ["久坐", "轻度活跃", "中度活跃", "高度活跃"],
                    index=["久坐", "轻度活跃", "中度活跃", "高度活跃"].index(user_profile.activity_level) if user_profile.activity_level in ["久坐", "轻度活跃", "中度活跃", "高度活跃"] else 1)
                
                fitness_goal = st.selectbox("健身目标",
                    ["减重", "增肌", "保持健康", "提高耐力", "增强力量"],
                    index=["减重", "增肌", "保持健康", "提高耐力", "增强力量"].index(user_profile.fitness_goal) if user_profile.fitness_goal in ["减重", "增肌", "保持健康", "提高耐力", "增强力量"] else 2)
                
                health_conditions = st.text_area("健康状况", value=user_profile.health_conditions or "", 
                                                placeholder="请描述任何健康问题或过敏...")
                dietary_preferences = st.text_area("饮食偏好", value=user_profile.dietary_preferences or "",
                                                  placeholder="素食、无乳糖、无麸质等...")
                
                if st.form_submit_button("更新健康偏好"):
                    preferences_data = {
                        'activity_level': activity_level,
                        'fitness_goal': fitness_goal,
                        'health_conditions': health_conditions,
                        'dietary_preferences': dietary_preferences
                    }
                    if st.session_state.db.update_user_profile(preferences_data):
                        st.success("健康偏好更新成功！")
                        st.rerun()
                    else:
                        st.error("更新失败，请重试")

def render_analytics_page():
    """渲染数据分析页面"""
    st.title("📊 健康数据分析")
    
    # 时间范围选择
    col1, col2 = st.columns([1, 3])
    with col1:
        time_range = st.selectbox("时间范围", ["最近7天", "最近30天", "最近90天"])
        days_map = {"最近7天": 7, "最近30天": 30, "最近90天": 90}
        selected_days = days_map[time_range]
    
    # 数据类型选择
    with col2:
        data_types = st.multiselect("数据类型", 
                                   ["体重", "运动", "心情", "睡眠"], 
                                   default=["体重", "运动", "心情"])
    
    st.markdown("---")
    
    # 显示图表
    if "体重" in data_types:
        st.subheader("📈 体重趋势分析")
        weight_records = st.session_state.db.get_health_records('weight', days=selected_days)
        if weight_records:
            weight_chart = st.session_state.visualizer.create_weight_trend_chart(weight_records)
            st.plotly_chart(weight_chart, use_container_width=True)
        else:
            st.info("该时间范围内无体重数据")
    
    if "运动" in data_types:
        st.subheader("🏃 运动频率分析")
        exercise_records = st.session_state.db.get_health_records('exercise', days=selected_days)
        if exercise_records:
            exercise_chart = st.session_state.visualizer.create_exercise_frequency_chart(exercise_records)
            st.plotly_chart(exercise_chart, use_container_width=True)
        else:
            st.info("该时间范围内无运动数据")
    
    if "心情" in data_types:
        st.subheader("😊 心情变化分析")
        mood_records = st.session_state.db.get_health_records('mood', days=selected_days)
        if mood_records:
            mood_chart = st.session_state.visualizer.create_mood_trend_chart(mood_records)
            st.plotly_chart(mood_chart, use_container_width=True)
        else:
            st.info("该时间范围内无心情数据")
    
    # 健康洞察
    st.markdown("---")
    st.session_state.dashboard.render_health_insights()

def render_settings_page():
    """渲染设置页面"""
    st.title("⚙️ 应用设置")
    
    tab1, tab2, tab3 = st.tabs(["🤖 AI设置", "📱 应用设置", "💾 数据管理"])
    
    with tab1:
        st.subheader("AI助手设置")
        
        # OpenAI设置
        api_key = st.text_input("OpenAI API Key", 
                               value=os.getenv("OPENAI_API_KEY", ""), 
                               type="password",
                               help="设置OpenAI API密钥以使用AI功能")
        
        api_base = st.text_input("API Base URL", 
                                value=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
                                help="API基础URL，可使用代理服务")
        
        model_name = st.selectbox("AI模型", 
                                 ["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
                                 help="选择使用的AI模型")
        
        if st.button("保存AI设置"):
            # 这里可以保存到配置文件
            st.success("AI设置已保存")
    
    with tab2:
        st.subheader("界面设置")
        
        theme = st.selectbox("主题", ["浅色", "深色", "自动"])
        language = st.selectbox("语言", ["中文", "English"])
        
        st.subheader("通知设置")
        enable_reminders = st.checkbox("启用提醒", value=True)
        reminder_time = st.time_input("提醒时间", value=datetime.strptime("09:00", "%H:%M").time())
        
        if st.button("保存应用设置"):
            st.success("应用设置已保存")
    
    with tab3:
        st.subheader("数据管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**备份数据**")
            if st.button("导出数据"):
                # 实现数据导出功能
                st.success("数据导出功能开发中...")
        
        with col2:
            st.markdown("**清除数据**")
            if st.button("清除所有数据", type="secondary"):
                st.warning("此操作将删除所有数据，请谨慎操作！")
        
        st.markdown("---")
        st.subheader("关于应用")
        st.info("""
        **智能健康助手 v1.0**
        
        这是一个集成了AI技术的个人健康管理工具，包含：
        - 🤖 AI健康咨询
        - 📊 数据可视化
        - 🎯 目标管理
        - 💾 数据持久化
        
        开发者：智能健康团队
        """)

def main():
    """主函数"""
    # 初始化应用
    initialize_app()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据页面状态渲染对应页面
    page = st.session_state.page
    
    if page == 'dashboard':
        render_dashboard_page()
    elif page == 'ai_chat':
        render_ai_chat_page()
    elif page == 'goals':
        render_goals_page()
    elif page == 'profile':
        render_profile_page()
    elif page == 'analytics':
        render_analytics_page()
    elif page == 'settings':
        render_settings_page()
    else:
        render_dashboard_page()

if __name__ == "__main__":
    main()

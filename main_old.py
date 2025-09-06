import streamlit as st
import json
import time
from typing import Dict, Any
from agents import HealthAssistant

# 页面配置
st.set_page_config(
    page_title="智能健康助手",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化健康助手
@st.cache_resource
def init_health_assistant():
    """初始化健康助手（缓存以提高性能）"""
    try:
        return HealthAssistant()
    except Exception as e:
        st.error(f"初始化健康助手失败: {e}")
        return None

def main():
    """主应用函数"""
    st.title("🏥 智能健康助手")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 功能选择")
        mode = st.radio(
            "选择使用模式",
            ["💬 智能对话", "📋 快速规划"],
            help="智能对话模式支持自然语言交流，快速规划模式提供结构化表单"
        )
        
        st.markdown("---")
        st.header("ℹ️ 功能说明")
        st.markdown("""
        **🏋️ 健身教练**: 制定个性化运动计划
        
        **🍎 营养师**: 提供饮食营养建议
        
        **🧘 心理健康顾问**: 压力管理和心理健康指导
        """)
        
        st.markdown("---")
        st.warning("⚠️ 本助手仅提供建议，不能替代专业医疗咨询")

    # 初始化健康助手
    health_assistant = init_health_assistant()
    if health_assistant is None:
        st.error("健康助手初始化失败，请检查配置")
        return

    if mode == "💬 智能对话":
        chat_mode(health_assistant)
    else:
        quick_planning_mode(health_assistant)


def chat_mode(health_assistant):
    """智能对话模式"""
    st.header("💬 智能对话模式")
    st.markdown("与我自然对话，我会为您提供专业的健康建议！")
    
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "您好！我是您的智能健康助手 🏥\n\n我的团队包括：\n- 🏋️ **健身教练**：制定运动计划\n- 🍎 **营养师**：提供饮食建议\n- 🧘 **心理健康顾问**：压力管理指导\n\n请告诉我您需要什么帮助？"
            }
        ]

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成助手回复
        with st.chat_message("assistant"):
            with st.spinner("正在为您生成专业建议..."):
                try:
                    responses = health_assistant.process_request(prompt)
                    
                    if responses:
                        full_response = ""
                        for response in responses:
                            agent_name = {
                                "fitness": "🏋️ 健身教练",
                                "nutrition": "🍎 营养师", 
                                "wellness": "🧘 心理健康顾问"
                            }.get(response["agent"], response["agent"])
                            
                            full_response += f"**{agent_name}**:\n\n{response['content']}\n\n---\n\n"
                        
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        error_msg = "抱歉，我现在无法处理您的请求。请稍后再试。"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
                except Exception as e:
                    error_msg = f"处理请求时出现错误: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def quick_planning_mode(health_assistant):
    """快速规划模式"""
    st.header("📋 快速健康规划")
    st.markdown("填写下面的表单，我将为您生成个性化的健康计划")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["🏋️ 健身计划", "🍎 营养计划", "🧘 综合健康"])
    
    with tab1:
        fitness_planning_form(health_assistant)
    
    with tab2:
        nutrition_planning_form(health_assistant)
    
    with tab3:
        comprehensive_planning_form(health_assistant)


def fitness_planning_form(health_assistant):
    """健身计划表单"""
    st.subheader("🏋️ 个性化健身计划")
    
    with st.form("fitness_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("年龄", min_value=1, max_value=120, value=30)
            weight = st.number_input("体重 (kg)", min_value=1.0, value=70.0)
            height = st.number_input("身高 (cm)", min_value=1.0, value=170.0)
            gender = st.selectbox("性别", ["男", "女", "其他"])
        
        with col2:
            primary_goal = st.selectbox(
                "主要目标",
                ["减重", "增肌", "耐力提升", "综合健身", "康复训练"]
            )
            activity_level = st.selectbox(
                "当前活动水平",
                ["久坐不动", "轻度活跃", "中度活跃", "高度活跃"]
            )
            workout_duration = st.slider("希望的锻炼时长 (分钟)", 15, 120, 45, 15)
        
        workout_preferences = st.multiselect(
            "运动偏好",
            ["有氧运动", "力量训练", "瑜伽", "普拉提", "柔韧性训练", "HIIT", "户外运动"]
        )
        
        health_conditions = st.text_area("健康状况或运动限制 (可选)")
        
        submitted = st.form_submit_button("生成健身计划", type="primary")
        
        if submitted:
            user_data = {
                "age": age,
                "weight": weight,
                "height": height,
                "gender": gender,
                "primary_goal": primary_goal,
                "activity_level": activity_level,
                "workout_duration": workout_duration,
                "workout_preferences": workout_preferences,
                "health_conditions": health_conditions
            }
            
            generate_fitness_plan(health_assistant, user_data)


def nutrition_planning_form(health_assistant):
    """营养计划表单"""
    st.subheader("🍎 个性化营养计划")
    
    with st.form("nutrition_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            primary_goal = st.selectbox(
                "营养目标",
                ["减重", "增肌", "维持健康", "增强免疫力", "改善消化"]
            )
            dietary_preferences = st.selectbox(
                "饮食偏好",
                ["无特殊要求", "素食", "纯素", "生酮饮食", "地中海饮食", "低糖饮食"]
            )
        
        with col2:
            allergies = st.text_input("食物过敏 (用逗号分隔)")
            cooking_time = st.selectbox(
                "可用烹饪时间",
                ["很少时间 (<15分钟)", "适中时间 (15-30分钟)", "充足时间 (>30分钟)"]
            )
        
        meal_frequency = st.slider("每日用餐次数", 3, 6, 3)
        water_intake = st.slider("每日饮水量 (杯)", 4, 12, 8)
        
        special_requirements = st.text_area("特殊营养需求或限制 (可选)")
        
        submitted = st.form_submit_button("生成营养计划", type="primary")
        
        if submitted:
            user_data = {
                "primary_goal": primary_goal,
                "dietary_preferences": dietary_preferences,
                "allergies": allergies,
                "cooking_time": cooking_time,
                "meal_frequency": meal_frequency,
                "water_intake": water_intake,
                "special_requirements": special_requirements
            }
            
            generate_nutrition_plan(health_assistant, user_data)


def comprehensive_planning_form(health_assistant):
    """综合健康计划表单"""
    st.subheader("🧘 综合健康规划")
    
    with st.form("comprehensive_form"):
        st.markdown("### 基本信息")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("年龄", min_value=1, max_value=120, value=30)
            lifestyle = st.selectbox(
                "生活方式",
                ["久坐办公", "轻度体力", "中度体力", "重度体力"]
            )
        
        with col2:
            stress_level = st.selectbox(
                "压力水平",
                ["低压力", "适中压力", "高压力", "极高压力"]
            )
            sleep_quality = st.selectbox(
                "睡眠质量",
                ["很好", "良好", "一般", "较差", "很差"]
            )
        
        st.markdown("### 健康目标")
        health_goals = st.multiselect(
            "选择您的健康目标",
            ["体重管理", "增强体能", "改善睡眠", "压力管理", "提高免疫力", "改善心情", "增加能量"]
        )
        
        current_challenges = st.text_area("当前面临的健康挑战")
        
        submitted = st.form_submit_button("生成综合健康计划", type="primary")
        
        if submitted:
            user_data = {
                "age": age,
                "lifestyle": lifestyle,
                "stress_level": stress_level,
                "sleep_quality": sleep_quality,
                "health_goals": health_goals,
                "current_challenges": current_challenges
            }
            
            generate_comprehensive_plan(health_assistant, user_data)


def generate_fitness_plan(health_assistant, user_data):
    """生成健身计划"""
    with st.spinner("正在生成您的个性化健身计划..."):
        try:
            prompt = f"请为我制定一个健身计划，我的信息如下：{json.dumps(user_data, ensure_ascii=False)}"
            responses = health_assistant.process_request(prompt)
            
            if responses:
                for response in responses:
                    if response["agent"] == "fitness":
                        st.success("✅ 健身计划生成成功！")
                        st.markdown(response["content"])
                        break
            else:
                st.error("生成健身计划失败，请重试")
                
        except Exception as e:
            st.error(f"生成健身计划时出现错误: {e}")


def generate_nutrition_plan(health_assistant, user_data):
    """生成营养计划"""
    with st.spinner("正在生成您的个性化营养计划..."):
        try:
            prompt = f"请为我制定一个营养计划，我的信息如下：{json.dumps(user_data, ensure_ascii=False)}"
            responses = health_assistant.process_request(prompt)
            
            if responses:
                for response in responses:
                    if response["agent"] == "nutrition":
                        st.success("✅ 营养计划生成成功！")
                        st.markdown(response["content"])
                        break
            else:
                st.error("生成营养计划失败，请重试")
                
        except Exception as e:
            st.error(f"生成营养计划时出现错误: {e}")


def generate_comprehensive_plan(health_assistant, user_data):
    """生成综合健康计划"""
    with st.spinner("正在生成您的综合健康计划..."):
        try:
            prompt = f"请为我制定一个综合健康计划，包括健身、营养和心理健康建议。我的信息如下：{json.dumps(user_data, ensure_ascii=False)}"
            responses = health_assistant.process_request(prompt)
            
            if responses:
                st.success("✅ 综合健康计划生成成功！")
                for response in responses:
                    agent_name = {
                        "fitness": "🏋️ 健身建议",
                        "nutrition": "🍎 营养建议", 
                        "wellness": "🧘 心理健康建议"
                    }.get(response["agent"], response["agent"])
                    
                    st.markdown(f"### {agent_name}")
                    st.markdown(response["content"])
                    st.markdown("---")
            else:
                st.error("生成综合健康计划失败，请重试")
                
        except Exception as e:
            st.error(f"生成综合健康计划时出现错误: {e}")


if __name__ == "__main__":
    main()

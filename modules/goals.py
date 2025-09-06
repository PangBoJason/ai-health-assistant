"""
目标设定与跟踪模块 - SMART目标管理系统
"""
import streamlit as st
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from core.database import DatabaseManager, Goal
from modules.visualization import HealthVisualizer

class GoalManager:
    """目标管理类"""
    
    def __init__(self, db: DatabaseManager, visualizer: HealthVisualizer):
        self.db = db
        self.visualizer = visualizer
        
        # 预定义目标模板
        self.goal_templates = {
            "减重": {
                "category": "weight",
                "unit": "kg",
                "description": "通过健康饮食和规律运动达到理想体重",
                "default_target": 5.0,
                "default_days": 90
            },
            "增肌": {
                "category": "fitness",
                "unit": "kg",
                "description": "通过力量训练增加肌肉量",
                "default_target": 3.0,
                "default_days": 120
            },
            "跑步距离": {
                "category": "fitness",
                "unit": "km",
                "description": "提升跑步耐力，达到目标距离",
                "default_target": 10.0,
                "default_days": 60
            },
            "运动频率": {
                "category": "fitness",
                "unit": "次/周",
                "description": "养成规律运动的习惯",
                "default_target": 4.0,
                "default_days": 30
            },
            "睡眠质量": {
                "category": "wellness",
                "unit": "小时/天",
                "description": "保证充足的睡眠时间",
                "default_target": 8.0,
                "default_days": 30
            },
            "饮水量": {
                "category": "nutrition",
                "unit": "杯/天",
                "description": "养成充足饮水的习惯",
                "default_target": 8.0,
                "default_days": 30
            }
        }
    
    def render_goal_management_page(self):
        """渲染目标管理页面"""
        st.title("🎯 目标管理中心")
        
        # 顶部统计
        self._render_goal_stats()
        
        st.markdown("---")
        
        # 主要内容区域
        tab1, tab2, tab3 = st.tabs(["📝 设定新目标", "📊 我的目标", "🏆 已完成目标"])
        
        with tab1:
            self._render_new_goal_form()
        
        with tab2:
            self._render_active_goals()
        
        with tab3:
            self._render_completed_goals()
    
    def _render_goal_stats(self):
        """渲染目标统计"""
        active_goals = self.db.get_active_goals()
        completed_goals = self.db.session.query(Goal).filter_by(status='completed').all()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("活跃目标", len(active_goals))
        
        with col2:
            st.metric("已完成目标", len(completed_goals))
        
        with col3:
            # 计算平均完成度
            if active_goals:
                avg_progress = sum(
                    (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
                    for goal in active_goals
                ) / len(active_goals)
                st.metric("平均进度", f"{avg_progress:.1f}%")
            else:
                st.metric("平均进度", "0%")
        
        with col4:
            # 本月完成的目标数
            month_start = datetime.utcnow().replace(day=1)
            month_completed = len([g for g in completed_goals 
                                 if g.completed_at and g.completed_at >= month_start])
            st.metric("本月完成", month_completed)
    
    def _render_new_goal_form(self):
        """渲染新目标表单"""
        st.subheader("设定新目标")
        
        # 选择目标类型
        col1, col2 = st.columns([1, 1])
        
        with col1:
            goal_type = st.selectbox(
                "选择目标类型",
                list(self.goal_templates.keys()),
                help="选择预设目标类型，或选择'自定义'创建个性化目标"
            )
        
        with col2:
            is_custom = st.checkbox("自定义目标", help="创建完全自定义的目标")
        
        # 目标表单
        with st.form("new_goal_form", clear_on_submit=True):
            if is_custom:
                # 自定义目标
                title = st.text_input("目标标题", placeholder="例如：每天冥想10分钟")
                description = st.text_area("目标描述", placeholder="详细描述你的目标...")
                category = st.selectbox("目标分类", ["fitness", "nutrition", "weight", "wellness"])
                target_value = st.number_input("目标数值", min_value=0.1, step=0.1)
                unit = st.text_input("单位", placeholder="例如：kg, 次, 分钟")
                deadline_days = st.number_input("完成期限（天）", min_value=1, max_value=365, value=30)
            else:
                # 预设目标
                template = self.goal_templates[goal_type]
                title = st.text_input("目标标题", value=f"达成{goal_type}目标")
                description = st.text_area("目标描述", value=template["description"])
                category = template["category"]
                target_value = st.number_input(
                    f"目标数值 ({template['unit']})", 
                    min_value=0.1, 
                    value=template["default_target"],
                    step=0.1
                )
                unit = template["unit"]
                deadline_days = st.number_input(
                    "完成期限（天）", 
                    min_value=1, 
                    max_value=365, 
                    value=template["default_days"]
                )
            
            # 计算截止日期
            deadline = datetime.utcnow() + timedelta(days=deadline_days)
            st.write(f"📅 截止日期: {deadline.strftime('%Y年%m月%d日')}")
            
            # 提交按钮
            submitted = st.form_submit_button("🎯 创建目标", type="primary")
            
            if submitted:
                if title and description and target_value > 0:
                    success = self.db.create_goal(
                        title=title,
                        description=description,
                        category=category,
                        target_value=target_value,
                        unit=unit,
                        deadline=deadline
                    )
                    
                    if success:
                        st.success("🎉 目标创建成功！")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("目标创建失败，请重试")
                else:
                    st.error("请填写所有必填字段")
    
    def _render_active_goals(self):
        """渲染活跃目标"""
        st.subheader("活跃目标")
        
        active_goals = self.db.get_active_goals()
        
        if not active_goals:
            st.info("暂无活跃目标，去创建第一个目标吧！")
            return
        
        # 显示目标进度图表
        if len(active_goals) > 0:
            goal_chart = self.visualizer.create_goal_progress_chart(active_goals)
            st.plotly_chart(goal_chart, use_container_width=True)
        
        st.markdown("---")
        
        # 显示目标详情和操作
        for i, goal in enumerate(active_goals):
            with st.container():
                self._render_goal_card(goal, i)
                st.markdown("---")
    
    def _render_goal_card(self, goal: Goal, index: int):
        """渲染单个目标卡片"""
        # 计算进度和剩余时间
        progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        days_left = (goal.deadline - datetime.utcnow()).days
        
        # 目标状态颜色
        if progress >= 100:
            status_color = "🟢"
        elif progress >= 75:
            status_color = "🟡"
        elif progress >= 50:
            status_color = "🟠"
        else:
            status_color = "🔴"
        
        # 紧急程度
        if days_left < 0:
            urgency = "⏰ 已逾期"
            urgency_color = "red"
        elif days_left <= 3:
            urgency = "🚨 紧急"
            urgency_color = "red"
        elif days_left <= 7:
            urgency = "⚠️ 注意"
            urgency_color = "orange"
        else:
            urgency = f"📅 {days_left}天"
            urgency_color = "green"
        
        # 布局
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### {status_color} {goal.title}")
            st.write(goal.description)
            
            # 进度条
            st.progress(min(progress / 100, 1.0))
            st.caption(f"进度: {goal.current_value:.1f}/{goal.target_value:.1f} {goal.unit} ({progress:.1f}%)")
        
        with col2:
            st.markdown(f"**截止日期**")
            st.markdown(f"<span style='color: {urgency_color}'>{urgency}</span>", 
                       unsafe_allow_html=True)
            st.write(goal.deadline.strftime('%Y-%m-%d'))
        
        with col3:
            st.markdown("**操作**")
            
            # 更新进度
            new_value = st.number_input(
                "更新进度",
                min_value=0.0,
                max_value=goal.target_value * 1.5,  # 允许超出目标
                value=goal.current_value,
                step=0.1,
                key=f"goal_update_{goal.id}_{index}"
            )
            
            if st.button("更新", key=f"update_btn_{goal.id}_{index}"):
                if self.db.update_goal_progress(goal.id, new_value):
                    if new_value >= goal.target_value:
                        st.success("🎉 恭喜！目标达成！")
                        st.balloons()
                    else:
                        st.success("进度更新成功！")
                    st.rerun()
                else:
                    st.error("更新失败")
            
            # 暂停/取消目标
            if st.button("暂停", key=f"pause_btn_{goal.id}_{index}"):
                self._pause_goal(goal.id)
    
    def _render_completed_goals(self):
        """渲染已完成目标"""
        st.subheader("已完成目标")
        
        completed_goals = self.db.session.query(Goal).filter_by(status='completed').order_by(Goal.completed_at.desc()).all()
        
        if not completed_goals:
            st.info("还没有完成的目标，继续努力吧！")
            return
        
        # 成就统计
        self._render_achievement_stats(completed_goals)
        
        st.markdown("---")
        
        # 显示已完成目标列表
        for goal in completed_goals[:10]:  # 只显示最近10个
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"### 🏆 {goal.title}")
                    st.write(goal.description)
                
                with col2:
                    st.write("**完成时间**")
                    if goal.completed_at:
                        st.write(goal.completed_at.strftime('%Y-%m-%d'))
                    
                    # 计算完成用时
                    if goal.completed_at:
                        days_taken = (goal.completed_at - goal.created_at).days
                        st.caption(f"用时: {days_taken}天")
                
                with col3:
                    st.write("**最终成果**")
                    st.metric("", f"{goal.current_value:.1f} {goal.unit}")
                    
                    # 超额完成标识
                    if goal.current_value > goal.target_value:
                        over_achieve = (goal.current_value / goal.target_value - 1) * 100
                        st.success(f"超额 {over_achieve:.1f}%")
                
                st.markdown("---")
    
    def _render_achievement_stats(self, completed_goals: List[Goal]):
        """渲染成就统计"""
        col1, col2, col3, col4 = st.columns(4)
        
        # 按类别统计
        category_counts = {}
        for goal in completed_goals:
            category_counts[goal.category] = category_counts.get(goal.category, 0) + 1
        
        with col1:
            st.metric("总完成数", len(completed_goals))
        
        with col2:
            # 最多完成的类别
            if category_counts:
                top_category = max(category_counts, key=category_counts.get)
                st.metric("擅长领域", top_category)
            else:
                st.metric("擅长领域", "暂无")
        
        with col3:
            # 本月完成数
            month_start = datetime.utcnow().replace(day=1)
            month_completed = len([g for g in completed_goals 
                                 if g.completed_at and g.completed_at >= month_start])
            st.metric("本月完成", month_completed)
        
        with col4:
            # 平均完成时间
            if completed_goals:
                avg_days = sum(
                    (g.completed_at - g.created_at).days 
                    for g in completed_goals if g.completed_at
                ) / len(completed_goals)
                st.metric("平均用时", f"{avg_days:.0f}天")
            else:
                st.metric("平均用时", "0天")
    
    def _pause_goal(self, goal_id: int):
        """暂停目标"""
        try:
            goal = self.db.session.query(Goal).filter_by(id=goal_id).first()
            if goal:
                goal.status = 'paused'
                self.db.session.commit()
                st.success("目标已暂停")
                st.rerun()
        except Exception as e:
            st.error(f"暂停失败: {e}")
    
    def render_goal_quick_view(self):
        """渲染目标快速视图（用于仪表板）"""
        active_goals = self.db.get_active_goals()
        
        if not active_goals:
            st.info("暂无活跃目标")
            return
        
        # 显示最紧急的3个目标
        urgent_goals = sorted(active_goals, key=lambda g: g.deadline)[:3]
        
        for goal in urgent_goals:
            progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
            days_left = (goal.deadline - datetime.utcnow()).days
            
            with st.container():
                st.write(f"**{goal.title}**")
                st.progress(min(progress / 100, 1.0))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"进度: {progress:.1f}%")
                with col2:
                    st.caption(f"剩余: {days_left}天")
                
                st.markdown("---")
    
    def get_motivation_message(self) -> str:
        """获取激励消息"""
        active_goals = self.db.get_active_goals()
        
        if not active_goals:
            return "🎯 设定一个新目标，开始你的成长之旅！"
        
        # 检查即将到期的目标
        urgent_goals = [g for g in active_goals if (g.deadline - datetime.utcnow()).days <= 7]
        if urgent_goals:
            return f"⏰ 有 {len(urgent_goals)} 个目标即将到期，加油冲刺！"
        
        # 检查进度良好的目标
        good_progress_goals = [g for g in active_goals 
                              if (g.current_value / g.target_value * 100) >= 75]
        if good_progress_goals:
            return f"🚀 有 {len(good_progress_goals)} 个目标进展顺利，继续保持！"
        
        return "💪 每一步努力都在让你更接近目标，继续前进！"

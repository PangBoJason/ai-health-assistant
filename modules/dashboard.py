"""
仪表板概览模块 - 显示用户当前状态和快速操作
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List
from core.database import DatabaseManager, Goal
from modules.visualization import HealthVisualizer

class Dashboard:
    """仪表板类"""
    
    def __init__(self, db: DatabaseManager, visualizer: HealthVisualizer):
        self.db = db
        self.visualizer = visualizer
    
    def render_dashboard(self):
        """渲染主仪表板"""
        st.title("🏥 智能健康助手 - 今日概览")
        
        # 获取统计数据
        stats = self.db.get_dashboard_stats()
        
        # 显示指标卡片
        self.visualizer.display_metric_cards(stats)
        
        st.markdown("---")
        
        # 布局：左侧图表，右侧快速操作
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_charts_section()
        
        with col2:
            self._render_quick_actions()
        
        st.markdown("---")
        
        # 底部：目标进度和本周总结
        self._render_goals_and_summary()
    
    def _render_charts_section(self):
        """渲染图表区域"""
        st.subheader("📊 健康趋势")
        
        # 图表选项卡
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["体重趋势", "运动记录", "心情变化"])
        
        with chart_tab1:
            weight_records = self.db.get_health_records('weight', days=30)
            if weight_records:
                weight_chart = self.visualizer.create_weight_trend_chart(weight_records)
                st.plotly_chart(weight_chart, use_container_width=True)
            else:
                st.info("暂无体重记录，快去添加第一条记录吧！")
        
        with chart_tab2:
            exercise_records = self.db.get_health_records('exercise', days=30)
            if exercise_records:
                exercise_chart = self.visualizer.create_exercise_frequency_chart(exercise_records)
                st.plotly_chart(exercise_chart, use_container_width=True)
            else:
                st.info("暂无运动记录，开始记录你的运动吧！")
        
        with chart_tab3:
            mood_records = self.db.get_health_records('mood', days=30)
            if mood_records:
                mood_chart = self.visualizer.create_mood_trend_chart(mood_records)
                st.plotly_chart(mood_chart, use_container_width=True)
            else:
                st.info("暂无心情记录，记录今天的心情吧！")
    
    def _render_quick_actions(self):
        """渲染快速操作区域"""
        st.subheader("⚡ 快速操作")
        
        # 快速记录体重
        with st.expander("📏 记录体重", expanded=False):
            weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, step=0.1, key="quick_weight")
            if st.button("保存体重", key="save_weight"):
                if self.db.add_health_record('weight', f"{weight} kg", weight):
                    st.success("体重记录成功！")
                    st.rerun()
                else:
                    st.error("记录失败，请重试")
        
        # 快速记录运动
        with st.expander("🏃 记录运动", expanded=False):
            exercise_type = st.selectbox("运动类型", 
                                       ["跑步", "健身", "游泳", "瑜伽", "散步", "其他"],
                                       key="quick_exercise_type")
            duration = st.number_input("时长 (分钟)", min_value=1, max_value=300, step=1, key="quick_duration")
            if st.button("保存运动", key="save_exercise"):
                exercise_value = f"{exercise_type} {duration}分钟"
                if self.db.add_health_record('exercise', exercise_value, duration):
                    st.success("运动记录成功！")
                    st.rerun()
                else:
                    st.error("记录失败，请重试")
        
        # 快速记录心情
        with st.expander("😊 记录心情", expanded=False):
            mood_value = st.slider("心情指数", 1, 10, 5, key="quick_mood")
            mood_note = st.text_area("心情备注", placeholder="今天的感受...", key="quick_mood_note")
            if st.button("保存心情", key="save_mood"):
                if self.db.add_health_record('mood', f"心情: {mood_value}/10", mood_value, mood_note):
                    st.success("心情记录成功！")
                    st.rerun()
                else:
                    st.error("记录失败，请重试")
        
        # 快速设定目标
        with st.expander("🎯 设定目标", expanded=False):
            if st.button("前往目标管理", key="goto_goals"):
                st.session_state.page = "goals"
                st.rerun()
    
    def _render_goals_and_summary(self):
        """渲染目标和总结区域"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 活跃目标")
            active_goals = self.db.get_active_goals()
            
            if active_goals:
                # 显示前3个最紧急的目标
                for goal in active_goals[:3]:
                    progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
                    
                    # 计算剩余天数
                    days_left = (goal.deadline - datetime.utcnow()).days
                    
                    with st.container():
                        st.write(f"**{goal.title}**")
                        st.progress(min(progress / 100, 1.0))
                        st.caption(f"进度: {progress:.1f}% | 剩余: {days_left}天")
                
                if len(active_goals) > 3:
                    st.caption(f"还有 {len(active_goals) - 3} 个目标...")
            else:
                st.info("暂无活跃目标，去设定一个新目标吧！")
        
        with col2:
            st.subheader("📅 本周总结")
            
            # 本周运动总结
            week_records = self.db.get_health_records('exercise', days=7)
            weekly_chart = self.visualizer.create_weekly_summary_chart(week_records)
            st.plotly_chart(weekly_chart, use_container_width=True)
            
            # 本周统计
            week_stats = self._calculate_week_stats()
            for stat_name, stat_value in week_stats.items():
                st.metric(stat_name, stat_value)
    
    def _calculate_week_stats(self) -> Dict[str, str]:
        """计算本周统计数据"""
        # 获取本周记录
        week_records = self.db.get_health_records(days=7)
        
        # 统计各类记录
        exercise_count = len([r for r in week_records if r.record_type == 'exercise'])
        mood_records = [r for r in week_records if r.record_type == 'mood']
        
        # 平均心情
        avg_mood = 0
        if mood_records:
            avg_mood = sum(r.numeric_value for r in mood_records) / len(mood_records)
        
        return {
            "运动次数": f"{exercise_count} 次",
            "平均心情": f"{avg_mood:.1f}/10" if avg_mood > 0 else "无记录"
        }
    
    def render_progress_bars(self):
        """渲染今日进度条"""
        st.subheader("📈 今日进度")
        
        # 获取今日目标完成情况
        today = datetime.utcnow().date()
        
        # 运动目标 (假设每日目标是30分钟)
        today_exercise = self.db.get_health_records('exercise', days=1)
        total_exercise_time = sum(r.numeric_value for r in today_exercise if r.numeric_value)
        exercise_progress = min(total_exercise_time / 30 * 100, 100)  # 目标30分钟
        
        st.write("🏃 运动目标 (30分钟)")
        st.progress(exercise_progress / 100)
        st.caption(f"已完成: {total_exercise_time:.0f}分钟 ({exercise_progress:.1f}%)")
        
        # 饮水目标 (假设每日8杯水)
        today_water = self.db.get_health_records('water', days=1)
        water_count = len(today_water)
        water_progress = min(water_count / 8 * 100, 100)
        
        st.write("💧 饮水目标 (8杯)")
        st.progress(water_progress / 100)
        st.caption(f"已完成: {water_count}杯 ({water_progress:.1f}%)")
    
    def render_health_insights(self):
        """渲染健康洞察"""
        st.subheader("💡 健康洞察")
        
        # 基于数据给出简单建议
        insights = self._generate_insights()
        
        for insight in insights:
            st.info(insight)
    
    def _generate_insights(self) -> List[str]:
        """生成健康洞察"""
        insights = []
        
        # 分析运动频率
        week_exercises = len(self.db.get_health_records('exercise', days=7))
        if week_exercises < 3:
            insights.append("🏃 本周运动次数较少，建议增加到每周3-5次运动")
        elif week_exercises >= 5:
            insights.append("🎉 本周运动频率很棒，继续保持！")
        
        # 分析心情趋势
        mood_records = self.db.get_health_records('mood', days=7)
        if mood_records:
            avg_mood = sum(r.numeric_value for r in mood_records) / len(mood_records)
            if avg_mood < 5:
                insights.append("😟 最近心情偏低，建议多做一些放松活动")
            elif avg_mood >= 7:
                insights.append("😊 最近心情不错，保持积极的生活态度！")
        
        # 体重趋势分析
        weight_records = self.db.get_health_records('weight', days=14)
        if len(weight_records) >= 2:
            recent_weight = weight_records[0].numeric_value
            older_weight = weight_records[-1].numeric_value
            weight_change = recent_weight - older_weight
            
            if abs(weight_change) > 1:
                direction = "增加" if weight_change > 0 else "减少"
                insights.append(f"⚖️ 近期体重{direction}了{abs(weight_change):.1f}kg，注意饮食和运动平衡")
        
        if not insights:
            insights.append("📊 继续记录数据，我们将为您提供更多个性化建议")
        
        return insights

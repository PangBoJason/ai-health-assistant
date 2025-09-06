"""
健康数据可视化模块 - 使用Plotly创建交互式图表
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import streamlit as st
from core.database import HealthRecord

class HealthVisualizer:
    """健康数据可视化类"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'success': '#2ca02c',
            'warning': '#ff7f0e',
            'danger': '#d62728',
            'info': '#17becf'
        }
    
    def create_weight_trend_chart(self, weight_records: List[HealthRecord]) -> go.Figure:
        """创建体重变化趋势图"""
        if not weight_records:
            return self._empty_chart("暂无体重数据")
        
        # 准备数据
        dates = [record.date.strftime('%Y-%m-%d') for record in weight_records]
        weights = [record.numeric_value for record in weight_records]
        
        # 创建图表
        fig = go.Figure()
        
        # 添加折线图
        fig.add_trace(go.Scatter(
            x=dates,
            y=weights,
            mode='lines+markers',
            name='体重 (kg)',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=8),
            hovertemplate='日期: %{x}<br>体重: %{y:.1f} kg<extra></extra>'
        ))
        
        # 添加趋势线
        if len(weights) > 1:
            # 简单的线性趋势
            from scipy import stats
            import numpy as np
            x_numeric = list(range(len(weights)))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, weights)
            trend_line = [slope * x + intercept for x in x_numeric]
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend_line,
                mode='lines',
                name='趋势线',
                line=dict(color=self.colors['warning'], width=2, dash='dash'),
                hovertemplate='趋势: %{y:.1f} kg<extra></extra>'
            ))
        
        # 设置布局
        fig.update_layout(
            title='体重变化趋势',
            xaxis_title='日期',
            yaxis_title='体重 (kg)',
            hovermode='x unified',
            showlegend=True,
            height=400
        )
        
        return fig
    
    def create_exercise_frequency_chart(self, exercise_records: List[HealthRecord]) -> go.Figure:
        """创建运动频率图表"""
        if not exercise_records:
            return self._empty_chart("暂无运动数据")
        
        # 按日期统计运动次数
        exercise_by_date = {}
        for record in exercise_records:
            date_str = record.date.strftime('%Y-%m-%d')
            exercise_by_date[date_str] = exercise_by_date.get(date_str, 0) + 1
        
        dates = list(exercise_by_date.keys())
        frequencies = list(exercise_by_date.values())
        
        # 创建柱状图
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=frequencies,
            name='运动次数',
            marker_color=self.colors['success'],
            hovertemplate='日期: %{x}<br>运动次数: %{y}<extra></extra>'
        ))
        
        # 设置布局
        fig.update_layout(
            title='运动频率统计',
            xaxis_title='日期',
            yaxis_title='运动次数',
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_mood_trend_chart(self, mood_records: List[HealthRecord]) -> go.Figure:
        """创建心情趋势图"""
        if not mood_records:
            return self._empty_chart("暂无心情数据")
        
        dates = [record.date.strftime('%Y-%m-%d') for record in mood_records]
        moods = [record.numeric_value for record in mood_records]
        
        # 创建图表
        fig = go.Figure()
        
        # 添加填充区域图
        fig.add_trace(go.Scatter(
            x=dates,
            y=moods,
            mode='lines+markers',
            name='心情指数',
            line=dict(color=self.colors['info'], width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(23, 190, 207, 0.1)',
            hovertemplate='日期: %{x}<br>心情: %{y}/10<extra></extra>'
        ))
        
        # 添加平均线
        if moods:
            avg_mood = sum(moods) / len(moods)
            fig.add_hline(
                y=avg_mood,
                line_dash="dash",
                line_color=self.colors['warning'],
                annotation_text=f"平均: {avg_mood:.1f}"
            )
        
        # 设置布局
        fig.update_layout(
            title='心情变化趋势',
            xaxis_title='日期',
            yaxis_title='心情指数 (1-10)',
            yaxis=dict(range=[0, 10]),
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def create_goal_progress_chart(self, goals: List) -> go.Figure:
        """创建目标进度图表"""
        if not goals:
            return self._empty_chart("暂无目标数据")
        
        goal_names = []
        progress_percentages = []
        colors = []
        
        for goal in goals:
            goal_names.append(goal.title)
            progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
            progress_percentages.append(min(progress, 100))  # 限制在100%
            
            # 根据进度设置颜色
            if progress >= 100:
                colors.append(self.colors['success'])
            elif progress >= 75:
                colors.append(self.colors['info'])
            elif progress >= 50:
                colors.append(self.colors['warning'])
            else:
                colors.append(self.colors['danger'])
        
        # 创建水平柱状图
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=progress_percentages,
            y=goal_names,
            orientation='h',
            marker_color=colors,
            hovertemplate='目标: %{y}<br>进度: %{x:.1f}%<extra></extra>'
        ))
        
        # 设置布局
        fig.update_layout(
            title='目标完成进度',
            xaxis_title='完成百分比 (%)',
            yaxis_title='目标',
            xaxis=dict(range=[0, 100]),
            height=max(400, len(goals) * 50),
            showlegend=False
        )
        
        return fig
    
    def create_weekly_summary_chart(self, records: List[HealthRecord]) -> go.Figure:
        """创建周度总结图表"""
        # 准备一周的数据
        today = datetime.now()
        week_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        week_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        # 统计每天的运动次数
        exercise_counts = []
        for date_str in week_dates:
            count = sum(1 for r in records if 
                       r.record_type == 'exercise' and 
                       r.date.strftime('%Y-%m-%d') == date_str)
            exercise_counts.append(count)
        
        # 创建图表
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=week_labels,
            y=exercise_counts,
            name='运动次数',
            marker_color=[self.colors['success'] if count > 0 else self.colors['danger'] 
                         for count in exercise_counts],
            hovertemplate='%{x}<br>运动次数: %{y}<extra></extra>'
        ))
        
        # 设置布局
        fig.update_layout(
            title='本周运动概览',
            xaxis_title='日期',
            yaxis_title='运动次数',
            showlegend=False,
            height=300
        )
        
        return fig
    
    def _empty_chart(self, message: str) -> go.Figure:
        """创建空数据图表"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400
        )
        
        return fig
    
    def display_metric_cards(self, stats: Dict[str, Any]):
        """显示指标卡片"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            weight_delta = None
            if stats.get('current_weight', 0) > 0:
                st.metric(
                    "当前体重", 
                    f"{stats.get('current_weight', 0):.1f} kg",
                    delta=weight_delta
                )
            else:
                st.metric("当前体重", "未记录", delta=None)
        
        with col2:
            today_ex = stats.get('today_exercises', 0)
            st.metric(
                "今日运动", 
                f"{today_ex} 次",
                delta=f"+{today_ex}" if today_ex > 0 else None
            )
        
        with col3:
            week_ex = stats.get('week_exercises', 0)
            st.metric(
                "本周运动", 
                f"{week_ex} 次",
                delta=f"目标: 3-5次"
            )
        
        with col4:
            mood = stats.get('latest_mood', 5)
            mood_emoji = self._get_mood_emoji(mood)
            st.metric(
                "心情指数", 
                f"{mood_emoji} {mood}/10",
                delta=None
            )
    
    def _get_mood_emoji(self, mood: float) -> str:
        """根据心情值返回对应表情"""
        if mood >= 8:
            return "😄"
        elif mood >= 6:
            return "😊"
        elif mood >= 4:
            return "😐"
        elif mood >= 2:
            return "😟"
        else:
            return "😢"

"""
数据持久化模块 - 使用SQLite + SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

Base = declarative_base()

class UserProfile(Base):
    """用户档案表"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    height = Column(Float)  # cm
    weight = Column(Float)  # kg
    activity_level = Column(String(50))
    fitness_goal = Column(String(100))
    health_conditions = Column(Text)
    dietary_preferences = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HealthRecord(Base):
    """健康记录表"""
    __tablename__ = 'health_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, default=1)
    record_type = Column(String(50))  # 'weight', 'exercise', 'mood', 'sleep', 'water'
    value = Column(String(500))
    numeric_value = Column(Float)  # 用于数值类型的记录
    notes = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    """目标管理表"""
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, default=1)
    title = Column(String(200))
    description = Column(Text)
    category = Column(String(50))  # 'fitness', 'nutrition', 'weight', 'wellness'
    target_value = Column(Float)
    current_value = Column(Float, default=0)
    unit = Column(String(50))
    deadline = Column(DateTime)
    status = Column(String(20), default='active')  # active, completed, paused, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/health_assistant.db"):
        # 确保data目录存在
        Path("data").mkdir(exist_ok=True)
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # 初始化默认用户
        self._init_default_user()
    
    def _init_default_user(self):
        """初始化默认用户"""
        existing_user = self.session.query(UserProfile).filter_by(id=1).first()
        if not existing_user:
            default_user = UserProfile(
                id=1,
                name="用户",
                age=25,
                gender="未设置",
                height=170.0,
                weight=65.0,
                activity_level="轻度活跃",
                fitness_goal="保持健康"
            )
            self.session.add(default_user)
            self.session.commit()
    
    # 用户档案相关操作
    def get_user_profile(self, user_id: int = 1) -> Optional[UserProfile]:
        """获取用户档案"""
        return self.session.query(UserProfile).filter_by(id=user_id).first()
    
    def update_user_profile(self, user_data: Dict[str, Any], user_id: int = 1) -> bool:
        """更新用户档案"""
        try:
            user = self.session.query(UserProfile).filter_by(id=user_id).first()
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"更新用户档案失败: {e}")
            return False
    
    # 健康记录相关操作
    def add_health_record(self, record_type: str, value: str, numeric_value: float = None, 
                         notes: str = "", user_id: int = 1) -> bool:
        """添加健康记录"""
        try:
            record = HealthRecord(
                user_id=user_id,
                record_type=record_type,
                value=value,
                numeric_value=numeric_value,
                notes=notes
            )
            self.session.add(record)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"添加健康记录失败: {e}")
            return False
    
    def get_health_records(self, record_type: str = None, days: int = 30, 
                          user_id: int = 1) -> List[HealthRecord]:
        """获取健康记录"""
        query = self.session.query(HealthRecord).filter_by(user_id=user_id)
        
        if record_type:
            query = query.filter_by(record_type=record_type)
        
        # 获取最近N天的记录
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(HealthRecord.date >= start_date)
        
        return query.order_by(HealthRecord.date.desc()).all()
    
    def get_latest_record(self, record_type: str, user_id: int = 1) -> Optional[HealthRecord]:
        """获取最新的某类型记录"""
        return self.session.query(HealthRecord).filter_by(
            user_id=user_id, 
            record_type=record_type
        ).order_by(HealthRecord.date.desc()).first()
    
    # 目标管理相关操作
    def create_goal(self, title: str, description: str, category: str, 
                   target_value: float, unit: str, deadline: datetime, 
                   user_id: int = 1) -> bool:
        """创建新目标"""
        try:
            goal = Goal(
                user_id=user_id,
                title=title,
                description=description,
                category=category,
                target_value=target_value,
                unit=unit,
                deadline=deadline
            )
            self.session.add(goal)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"创建目标失败: {e}")
            return False
    
    def get_active_goals(self, user_id: int = 1) -> List[Goal]:
        """获取活跃目标"""
        return self.session.query(Goal).filter_by(
            user_id=user_id, 
            status='active'
        ).order_by(Goal.deadline.asc()).all()
    
    def update_goal_progress(self, goal_id: int, current_value: float) -> bool:
        """更新目标进度"""
        try:
            goal = self.session.query(Goal).filter_by(id=goal_id).first()
            if goal:
                goal.current_value = current_value
                
                # 检查是否完成
                if current_value >= goal.target_value:
                    goal.status = 'completed'
                    goal.completed_at = datetime.utcnow()
                
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"更新目标进度失败: {e}")
            return False
    
    def get_dashboard_stats(self, user_id: int = 1) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        try:
            # 获取最新体重
            latest_weight = self.get_latest_record('weight', user_id)
            
            # 获取今日运动记录
            today = datetime.utcnow().date()
            today_exercises = self.session.query(HealthRecord).filter(
                HealthRecord.user_id == user_id,
                HealthRecord.record_type == 'exercise',
                HealthRecord.date >= today
            ).count()
            
            # 获取本周运动次数
            week_start = datetime.utcnow() - timedelta(days=7)
            week_exercises = self.session.query(HealthRecord).filter(
                HealthRecord.user_id == user_id,
                HealthRecord.record_type == 'exercise',
                HealthRecord.date >= week_start
            ).count()
            
            # 获取最新心情
            latest_mood = self.get_latest_record('mood', user_id)
            
            # 获取活跃目标数量
            active_goals_count = len(self.get_active_goals(user_id))
            
            return {
                'current_weight': latest_weight.numeric_value if latest_weight else 0,
                'today_exercises': today_exercises,
                'week_exercises': week_exercises,
                'latest_mood': latest_mood.numeric_value if latest_mood else 5,
                'active_goals': active_goals_count
            }
        except Exception as e:
            print(f"获取仪表板数据失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        self.session.close()

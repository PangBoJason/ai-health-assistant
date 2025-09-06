from typing import Annotated, TypedDict, List
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import random
import os
import json

load_dotenv()

# 获取API密钥
fitness_api_key = os.getenv("EXERCISE_API_KEY")
diet_api_key = os.getenv("DIET_API_KEY")


class FitnessPlanner:
    """健身计划生成器"""
    
    def __init__(self):
        self.base_url = "https://api.api-ninjas.com/v1/exercises"
        self.api_key = fitness_api_key
        
        # 预定义的运动数据（当API不可用时使用）
        self.exercise_database = {
            "strength": {
                "chest": [
                    {"name": "Push-ups", "instructions": "Start in plank position, lower body, push back up", "equipment": "None"},
                    {"name": "Chest Press", "instructions": "Lie on bench, press weights up from chest", "equipment": "Dumbbells"},
                    {"name": "Incline Push-ups", "instructions": "Hands on elevated surface, perform push-ups", "equipment": "Bench/Chair"}
                ],
                "back": [
                    {"name": "Pull-ups", "instructions": "Hang from bar, pull body up until chin over bar", "equipment": "Pull-up bar"},
                    {"name": "Bent-over Rows", "instructions": "Bend at waist, pull weights to chest", "equipment": "Dumbbells"},
                    {"name": "Superman", "instructions": "Lie face down, lift chest and legs off ground", "equipment": "None"}
                ],
                "legs": [
                    {"name": "Squats", "instructions": "Feet shoulder-width apart, lower hips, return to standing", "equipment": "None"},
                    {"name": "Lunges", "instructions": "Step forward, lower back knee, return to start", "equipment": "None"},
                    {"name": "Deadlifts", "instructions": "Feet hip-width apart, lift weight keeping back straight", "equipment": "Dumbbells"}
                ]
            },
            "cardio": [
                {"name": "Running", "instructions": "30-45 minutes moderate pace", "equipment": "None"},
                {"name": "Jump Rope", "instructions": "15-20 minutes with rest intervals", "equipment": "Jump rope"},
                {"name": "High Knees", "instructions": "30 seconds on, 30 seconds rest, repeat 10 times", "equipment": "None"}
            ],
            "flexibility": [
                {"name": "Cat-Cow Stretch", "instructions": "On hands and knees, arch and round spine", "equipment": "None"},
                {"name": "Downward Dog", "instructions": "Hands and feet on ground, form inverted V", "equipment": "None"},
                {"name": "Child's Pose", "instructions": "Kneel, sit back on heels, stretch arms forward", "equipment": "None"}
            ]
        }
    
    def fetch_exercises_from_api(self, muscle, exercise_type, difficulty="beginner"):
        """从API获取运动数据"""
        if not self.api_key:
            return None
            
        headers = {'X-Api-Key': self.api_key}
        params = {
            'type': exercise_type,
            'muscle': muscle,
            'difficulty': difficulty
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            print(f"API请求失败: {e}")
        return None
    
    def generate_workout_plan(self, user_data):
        """生成个性化健身计划"""
        goal = user_data.get("primary_goal", "general fitness").lower()
        activity_level = user_data.get("activity_level", "beginner").lower()
        workout_preferences = user_data.get("workout_preferences", [])
        workout_duration = user_data.get("workout_duration", 45)
        
        plan = []
        plan.append(f"🏋️ **个性化健身计划** (基于目标: {goal})")
        plan.append(f"⏱️ **建议时长**: {workout_duration}分钟")
        plan.append(f"📊 **难度等级**: {activity_level}")
        plan.append("")
        
        # 根据目标选择运动类型
        if "weight loss" in goal or "减重" in goal:
            plan.extend(self._create_weight_loss_plan(workout_preferences, activity_level))
        elif "muscle gain" in goal or "增肌" in goal:
            plan.extend(self._create_muscle_gain_plan(workout_preferences, activity_level))
        elif "endurance" in goal or "耐力" in goal:
            plan.extend(self._create_endurance_plan(workout_preferences, activity_level))
        else:
            plan.extend(self._create_general_fitness_plan(workout_preferences, activity_level))
        
        plan.append("")
        plan.append("⚠️ **注意事项**:")
        plan.append("- 运动前进行5-10分钟热身")
        plan.append("- 运动后进行拉伸放松")
        plan.append("- 如有身体不适请立即停止")
        plan.append("- 建议咨询专业教练指导")
        
        return "\n".join(plan)
    
    def _create_weight_loss_plan(self, preferences, level):
        """减重计划"""
        plan = ["🔥 **减重专项计划**", ""]
        
        # 有氧运动为主
        cardio_exercises = random.sample(self.exercise_database["cardio"], 2)
        plan.append("**有氧运动 (3-4次/周)**:")
        for i, exercise in enumerate(cardio_exercises, 1):
            plan.append(f"{i}. {exercise['name']}: {exercise['instructions']}")
        
        plan.append("")
        
        # 力量训练辅助
        strength_exercises = []
        for muscle_group in ["chest", "back", "legs"]:
            exercises = self.exercise_database["strength"][muscle_group]
            strength_exercises.append(random.choice(exercises))
        
        plan.append("**力量训练 (2-3次/周)**:")
        for i, exercise in enumerate(strength_exercises, 1):
            plan.append(f"{i}. {exercise['name']}: {exercise['instructions']}")
        
        return plan
    
    def _create_muscle_gain_plan(self, preferences, level):
        """增肌计划"""
        plan = ["💪 **增肌专项计划**", ""]
        
        plan.append("**力量训练 (4-5次/周)**:")
        exercise_count = 1
        for muscle_group, exercises in self.exercise_database["strength"].items():
            selected = random.sample(exercises, 2)
            plan.append(f"**{muscle_group.title()}训练:**")
            for exercise in selected:
                plan.append(f"{exercise_count}. {exercise['name']}: {exercise['instructions']}")
                exercise_count += 1
            plan.append("")
        
        return plan
    
    def _create_endurance_plan(self, preferences, level):
        """耐力计划"""
        plan = ["🏃 **耐力提升计划**", ""]
        
        cardio_exercises = self.exercise_database["cardio"]
        plan.append("**耐力训练 (4-5次/周)**:")
        for i, exercise in enumerate(cardio_exercises, 1):
            plan.append(f"{i}. {exercise['name']}: {exercise['instructions']}")
        
        return plan
    
    def _create_general_fitness_plan(self, preferences, level):
        """综合健身计划"""
        plan = ["🌟 **综合健身计划**", ""]
        
        # 混合训练
        plan.append("**每周训练安排**:")
        plan.append("周一/三/五: 力量训练")
        plan.append("周二/四: 有氧运动")
        plan.append("周六: 柔韧性训练")
        plan.append("周日: 休息")
        plan.append("")
        
        # 具体运动
        plan.append("**推荐运动**:")
        all_exercises = []
        
        # 选择各类运动
        for muscle_group in self.exercise_database["strength"]:
            all_exercises.append(random.choice(self.exercise_database["strength"][muscle_group]))
        
        all_exercises.extend(random.sample(self.exercise_database["cardio"], 2))
        all_exercises.extend(random.sample(self.exercise_database["flexibility"], 2))
        
        for i, exercise in enumerate(all_exercises, 1):
            plan.append(f"{i}. {exercise['name']}: {exercise['instructions']}")
        
        return plan


class NutritionPlanner:
    """营养计划生成器"""
    
    def __init__(self):
        self.base_url = "https://api.spoonacular.com"
        self.api_key = diet_api_key
        
        # 预定义的营养建议数据
        self.nutrition_database = {
            "weight_loss": {
                "principles": [
                    "创造热量缺口，每日减少300-500卡路里",
                    "增加蛋白质摄入，维持肌肉量",
                    "多吃高纤维食物，增加饱腹感",
                    "控制精制糖和加工食品摄入"
                ],
                "meals": [
                    {"meal": "早餐", "suggestion": "燕麦片+水果+坚果，或全麦面包+鸡蛋+牛奶"},
                    {"meal": "午餐", "suggestion": "瘦肉/鱼肉+蔬菜+糙米/全麦面条"},
                    {"meal": "晚餐", "suggestion": "蒸蛋/豆腐+大量蔬菜+少量主食"},
                    {"meal": "加餐", "suggestion": "苹果、酸奶或一小把坚果"}
                ]
            },
            "muscle_gain": {
                "principles": [
                    "增加热量摄入，每日增加300-500卡路里",
                    "高蛋白摄入，每公斤体重1.6-2.2g蛋白质",
                    "充足碳水化合物，支持训练能量",
                    "健康脂肪，占总热量20-30%"
                ],
                "meals": [
                    {"meal": "早餐", "suggestion": "鸡蛋+全麦面包+牛奶+香蕉"},
                    {"meal": "训练前", "suggestion": "香蕉+燕麦片，提供能量"},
                    {"meal": "训练后", "suggestion": "蛋白粉+水果，促进恢复"},
                    {"meal": "午餐", "suggestion": "鸡胸肉+糙米+蔬菜+牛油果"},
                    {"meal": "晚餐", "suggestion": "鱼肉+红薯+绿叶蔬菜"}
                ]
            },
            "general_health": {
                "principles": [
                    "均衡营养，多样化饮食",
                    "控制份量，适量进食",
                    "多吃新鲜蔬菜水果",
                    "充足水分摄入"
                ],
                "meals": [
                    {"meal": "早餐", "suggestion": "粗粮+蛋白质+水果"},
                    {"meal": "午餐", "suggestion": "瘦肉+蔬菜+全谷物"},
                    {"meal": "晚餐", "suggestion": "鱼类+蔬菜+少量主食"},
                    {"meal": "加餐", "suggestion": "坚果、水果或酸奶"}
                ]
            }
        }
    
    def generate_nutrition_plan(self, user_data):
        """生成营养计划"""
        goal = user_data.get("primary_goal", "general fitness").lower()
        dietary_preferences = user_data.get("dietary_preferences", "")
        
        plan = []
        plan.append("🍎 **个性化营养计划**")
        plan.append("")
        
        # 根据目标选择营养策略
        if "weight loss" in goal or "减重" in goal:
            nutrition_data = self.nutrition_database["weight_loss"]
            plan.append("🎯 **减重营养策略**")
        elif "muscle gain" in goal or "增肌" in goal:
            nutrition_data = self.nutrition_database["muscle_gain"]
            plan.append("🎯 **增肌营养策略**")
        else:
            nutrition_data = self.nutrition_database["general_health"]
            plan.append("🎯 **健康营养策略**")
        
        plan.append("")
        
        # 营养原则
        plan.append("**营养原则:**")
        for i, principle in enumerate(nutrition_data["principles"], 1):
            plan.append(f"{i}. {principle}")
        
        plan.append("")
        
        # 餐食建议
        plan.append("**每日餐食建议:**")
        for meal_info in nutrition_data["meals"]:
            plan.append(f"**{meal_info['meal']}**: {meal_info['suggestion']}")
        
        # 个性化建议
        if dietary_preferences:
            plan.append("")
            plan.append(f"**个人偏好考虑**: {dietary_preferences}")
        
        plan.append("")
        plan.append("💧 **水分摄入**: 每日8-10杯水")
        plan.append("⚠️ **注意**: 如有特殊疾病请咨询营养师")
        
        return "\n".join(plan)


class MentalWellnessCoach:
    """心理健康教练"""
    
    def __init__(self):
        self.wellness_tips = [
            "深呼吸练习：每天进行5-10分钟的深呼吸，有助于减压放松",
            "正念冥想：专注当下，观察自己的思绪和感受，不做评判",
            "感恩练习：每天记录3件值得感恩的事情，培养积极心态",
            "适度运动：有氧运动能释放内啡肽，改善情绪",
            "充足睡眠：保证7-9小时睡眠，有助于情绪稳定",
            "社交连接：与朋友家人保持联系，分享情感支持",
            "时间管理：合理安排时间，避免过度压力",
            "兴趣爱好：培养自己喜欢的活动，增加生活乐趣",
            "户外活动：多接触自然，阳光有助于改善心情",
            "学会说不：设定边界，避免过度承诺造成压力"
        ]
        
        self.stress_relief_techniques = [
            "渐进式肌肉放松：从脚趾到头部，逐一紧张和放松肌肉群",
            "4-7-8呼吸法：吸气4秒，屏气7秒，呼气8秒",
            "可视化放松：想象自己在宁静的地方，如海滩或森林",
            "热水澡或泡脚：温热的水能帮助肌肉放松",
            "听音乐：选择舒缓的音乐，让心情平静下来",
            "写日记：记录情感和想法，释放内心压力",
            "温和瑜伽：通过瑜伽姿势和呼吸练习放松身心",
            "芳香疗法：使用薰衣草等精油帮助放松",
            "暂时断网：给自己一些不被打扰的宁静时间"
        ]
    
    def generate_wellness_advice(self, user_data=None):
        """生成心理健康建议"""
        advice = []
        advice.append("🧘 **心理健康指导**")
        advice.append("")
        
        # 随机选择几个健康建议
        selected_tips = random.sample(self.wellness_tips, 3)
        advice.append("**今日健康贴士:**")
        for i, tip in enumerate(selected_tips, 1):
            advice.append(f"{i}. {tip}")
        
        advice.append("")
        
        # 压力缓解技巧
        selected_techniques = random.sample(self.stress_relief_techniques, 2)
        advice.append("**压力缓解技巧:**")
        for i, technique in enumerate(selected_techniques, 1):
            advice.append(f"{i}. {technique}")
        
        advice.append("")
        advice.append("🔔 **重要提醒:**")
        advice.append("- 如果情绪持续低落超过两周，建议寻求专业心理咨询")
        advice.append("- 心理健康和身体健康同样重要")
        advice.append("- 每个人的情况不同，找到适合自己的方法")
        
        return "\n".join(advice)


# 工具函数定义
@tool
def fitness_planning_tool(user_data: Annotated[dict, "用户的健身相关数据，包括目标、偏好等"]):
    """生成个性化健身计划的工具"""
    planner = FitnessPlanner()
    return planner.generate_workout_plan(user_data)


@tool
def nutrition_planning_tool(user_data: Annotated[dict, "用户的营养相关数据，包括目标、偏好等"]):
    """生成个性化营养计划的工具"""
    planner = NutritionPlanner()
    return planner.generate_nutrition_plan(user_data)


@tool
def wellness_advice_tool(user_data: Annotated[dict, "用户数据，可选"] = None):
    """提供心理健康建议的工具"""
    coach = MentalWellnessCoach()
    return coach.generate_wellness_advice(user_data)

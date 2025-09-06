"""
测试脚本 - 验证智能健康助手的基础功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tools():
    """测试工具函数"""
    print("🧪 测试工具函数...")
    
    try:
        from tools import FitnessPlanner, NutritionPlanner, MentalWellnessCoach
        
        # 测试健身规划器
        print("\n1. 测试健身规划器...")
        fitness_planner = FitnessPlanner()
        
        user_data = {
            "primary_goal": "weight loss",
            "activity_level": "beginner",
            "workout_preferences": ["cardio", "strength"],
            "workout_duration": 45
        }
        
        fitness_plan = fitness_planner.generate_workout_plan(user_data)
        print("✅ 健身计划生成成功")
        print(fitness_plan[:200] + "...")
        
        # 测试营养规划器
        print("\n2. 测试营养规划器...")
        nutrition_planner = NutritionPlanner()
        
        nutrition_plan = nutrition_planner.generate_nutrition_plan(user_data)
        print("✅ 营养计划生成成功")
        print(nutrition_plan[:200] + "...")
        
        # 测试心理健康教练
        print("\n3. 测试心理健康教练...")
        wellness_coach = MentalWellnessCoach()
        
        wellness_advice = wellness_coach.generate_wellness_advice()
        print("✅ 心理健康建议生成成功")
        print(wellness_advice[:200] + "...")
        
        print("\n🎉 所有工具测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False


def test_environment():
    """测试环境配置"""
    print("🔧 测试环境配置...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        
        if api_key and api_base:
            print("✅ API配置检测成功")
            print(f"API Base: {api_base}")
            print(f"API Key: {api_key[:10]}...")
            return True
        else:
            print("❌ API配置缺失，请检查.env文件")
            return False
            
    except Exception as e:
        print(f"❌ 环境配置测试失败: {e}")
        return False


def test_basic_functionality():
    """测试基础功能（无需API调用）"""
    print("🎯 测试基础功能...")
    
    # 测试数据结构
    print("\n1. 测试数据结构...")
    from tools import FitnessPlanner
    
    planner = FitnessPlanner()
    
    # 验证数据库结构
    assert "strength" in planner.exercise_database
    assert "cardio" in planner.exercise_database
    assert "flexibility" in planner.exercise_database
    
    print("✅ 数据结构正确")
    
    # 测试计划生成逻辑
    print("\n2. 测试计划生成逻辑...")
    
    test_cases = [
        {"primary_goal": "weight loss", "activity_level": "beginner"},
        {"primary_goal": "muscle gain", "activity_level": "intermediate"},
        {"primary_goal": "endurance improvement", "activity_level": "advanced"},
        {"primary_goal": "general fitness", "activity_level": "beginner"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        plan = planner.generate_workout_plan(test_case)
        assert len(plan) > 100  # 确保计划有足够内容
        print(f"✅ 测试案例 {i} 通过")
    
    print("🎉 基础功能测试全部通过！")
    return True


def main():
    """主测试函数"""
    print("🚀 智能健康助手 - 测试套件")
    print("="*50)
    
    # 测试环境
    env_ok = test_environment()
    
    # 测试工具
    tools_ok = test_tools()
    
    # 测试基础功能
    basic_ok = test_basic_functionality()
    
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print(f"环境配置: {'✅ 通过' if env_ok else '❌ 失败'}")
    print(f"工具功能: {'✅ 通过' if tools_ok else '❌ 失败'}")
    print(f"基础功能: {'✅ 通过' if basic_ok else '❌ 失败'}")
    
    if env_ok and tools_ok and basic_ok:
        print("\n🎉 所有测试通过！可以运行主应用了。")
        print("运行命令: streamlit run main.py")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和依赖。")


if __name__ == "__main__":
    main()

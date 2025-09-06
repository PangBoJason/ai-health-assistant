from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from dotenv import load_dotenv
import os
import json

from tools import fitness_planning_tool, nutrition_planning_tool, wellness_advice_tool

load_dotenv()

# 配置OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")

# 初始化LLM
llm = ChatOpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
    model="gpt-4o",
    temperature=0.7
)

# 内存保存器
memory = MemorySaver()

# 代理成员
members = ["fitness", "nutrition", "wellness"]
options = members + ["FINISH"]

# 系统提示词
system_prompt = f"""你是一个智能健康助手的督导员，负责管理以下专业助手之间的对话: {members}。

根据用户的请求，选择最合适的助手来处理任务：
- fitness: 处理健身、运动、锻炼相关的问题
- nutrition: 处理营养、饮食、餐食计划相关的问题  
- wellness: 处理心理健康、压力管理、生活方式相关的问题

规则：
1. 仔细分析用户的需求，选择最合适的助手
2. 如果需要多个助手协作，按逻辑顺序安排
3. 当所有必要的任务都完成后，返回 'FINISH'
4. 优先考虑用户的主要需求和目标

当前可选助手: {options}
"""

# 各个代理的提示词
fitness_agent_prompt = """你是一位专业的健身教练AI助手。你的任务是：
1. 分析用户的健身目标、身体状况和偏好
2. 制定个性化的运动计划
3. 提供专业的健身建议和指导
4. 确保运动计划的安全性和有效性

请根据用户提供的信息，使用健身规划工具生成合适的运动计划。
"""

nutrition_agent_prompt = """你是一位专业的营养师AI助手。你的任务是：
1. 分析用户的营养需求和目标
2. 制定个性化的饮食计划
3. 提供健康的营养建议
4. 考虑用户的饮食偏好和限制

请根据用户提供的信息，使用营养规划工具生成合适的饮食计划。
"""

wellness_agent_prompt = """你是一位专业的心理健康顾问AI助手。你的任务是：
1. 提供心理健康和压力管理建议
2. 分享放松和冥想技巧
3. 帮助用户建立健康的生活方式
4. 提供情绪支持和积极引导

请使用心理健康工具为用户提供有益的建议。
"""

# 创建各个代理
fitness_agent = create_react_agent(llm, tools=[fitness_planning_tool], state_modifier=fitness_agent_prompt)
nutrition_agent = create_react_agent(llm, tools=[nutrition_planning_tool], state_modifier=nutrition_agent_prompt)
wellness_agent = create_react_agent(llm, tools=[wellness_advice_tool], state_modifier=wellness_agent_prompt)

# 状态定义
class State(MessagesState):
    next: str


class Router(TypedDict):
    """路由器，选择下一个处理的助手"""
    next: str


# 代理节点函数
def fitness_node(state: State) -> Command[Literal["supervisor"]]:
    """健身代理节点"""
    result = fitness_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="fitness")
            ]
        },
        goto="supervisor",
    )


def nutrition_node(state: State) -> Command[Literal["supervisor"]]:
    """营养代理节点"""
    result = nutrition_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="nutrition")
            ]
        },
        goto="supervisor",
    )


def wellness_node(state: State) -> Command[Literal["supervisor"]]:
    """心理健康代理节点"""
    result = wellness_agent.invoke(state)
    return Command(
        update={
            "messages": [
                AIMessage(content=result["messages"][-1].content, name="wellness")
            ]
        },
        goto="supervisor",
    )


def supervisor_node(state: State) -> Command[str]:
    """督导员节点，决定下一步行动"""
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    
    if goto == "FINISH":
        goto = END
    
    return Command(goto=goto, update={"next": goto})


# 构建工作流图
def create_health_assistant_graph():
    """创建健康助手工作流图"""
    builder = StateGraph(State)
    
    # 添加节点
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("fitness", fitness_node)
    builder.add_node("nutrition", nutrition_node)
    builder.add_node("wellness", wellness_node)
    
    # 编译图
    graph = builder.compile(checkpointer=memory)
    return graph


class HealthAssistant:
    """智能健康助手主类"""
    
    def __init__(self):
        self.graph = create_health_assistant_graph()
        
    def process_request(self, user_input, thread_id="default"):
        """处理用户请求"""
        inputs = {
            "messages": [HumanMessage(content=user_input)]
        }
        
        config = {
            "configurable": {
                "thread_id": thread_id,
                "recursion_limit": 15
            }
        }
        
        # 流式处理
        responses = []
        for step in self.graph.stream(inputs, config=config):
            for key, value in step.items():
                if key != "supervisor" and "messages" in value:
                    messages = value["messages"]
                    for msg in messages:
                        if isinstance(msg, AIMessage):
                            responses.append({
                                "agent": key,
                                "content": msg.content
                            })
        
        return responses

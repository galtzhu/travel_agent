import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
# 🔴 变化 1: 导入 OpenAI 模型接口 (Qwen 兼容此接口)
from agno.models.openai import OpenAIChat
# 数据库和工具保持不变
from agno.db.postgres import PostgresDb
from tools.gaode_tool import GaodeToolkit
from tools.tomorrow_weather_tool import TomorrowWeatherToolkit

load_dotenv()

def get_env_var(key_name):
    """兼容本地和云端的 Key 读取助手"""
    try:
        return st.secrets[key_name]
    except (FileNotFoundError, KeyError):
        return os.getenv(key_name)

def get_travel_agent(session_id="default_session"):
    # --- 1. 读取 Key ---
    # 🔴 变化 2: 读取阿里云 Key
    qwen_key = get_env_var("DASHSCOPE_API_KEY") 
    
    gaode_key = get_env_var("GAODE_API_KEY")
    tomorrow_key = get_env_var("TOMORROW_API_KEY")
    db_url = get_env_var("DB_URL")

    # 检查 Key 是否齐全
    if not all([qwen_key, gaode_key, tomorrow_key, db_url]):
        raise ValueError("密钥缺失！请检查 .env 或 Streamlit Secrets，确保 DASHSCOPE_API_KEY 等已配置")

    # 注入环境变量供工具使用
    os.environ["GAODE_API_KEY"] = gaode_key
    os.environ["TOMORROW_API_KEY"] = tomorrow_key

    # 🔴 变化 3: 初始化 Qwen 模型 (通过 OpenAI 接口)
    model = OpenAIChat(
        id="qwen-plus", # 或者用能力更强的 "qwen-max"
        api_key=qwen_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", # 必填：阿里云的转接地址
    )
    
    # 数据库连接 (保持不变)
    db = PostgresDb(
        db_url=db_url,
        session_table="agent_sessions"
    )

    # 创建 Agent
    agent = Agent(
        model=model, # 👈 这里放入 Qwen
        session_id=session_id,
        db=db,
        add_history_to_context=True,
        tools=[GaodeToolkit(), TomorrowWeatherToolkit()],
        markdown=True,
        debug_mode=True, 
        description="你是一位拥有10年经验的高级私人旅行定制师...",
        instructions=[
            "1. **用户画像（核心）**：在开始规划前，必须确认：几人出行？有无老人小孩？偏好什么风格？如果用户没说，必须礼貌询问。",
            "2. **拒绝幻觉**：必须使用 `search_places` 查具体地点，使用 `hourly_weather` 查天气。",
            "3. **方案结构**：输出必须包含【👔衣、🥣食、🏠住/玩、🚗行】四个维度。",
            "4. **记忆利用**：如果用户之前已经说过是'4人亲子游'，绝对不要重复问。"
        ]
    )
    return agent

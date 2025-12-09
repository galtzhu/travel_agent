import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
# 🔴 关键变化 1：导入 PostgresDb 而不是 SqliteDb
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
    google_key = get_env_var("GOOGLE_API_KEY")
    gaode_key = get_env_var("GAODE_API_KEY")
    tomorrow_key = get_env_var("TOMORROW_API_KEY")
    
    # 🔴 关键变化 2：读取 DB_URL
    db_url = get_env_var("DB_URL") 

    # --- 2. 检查是否读取成功 ---
    # 🔴 关键变化 3：把 db_url 加入检查列表
    if not all([google_key, gaode_key, tomorrow_key, db_url]):
        raise ValueError("密钥缺失！请检查 .env 或 Streamlit Secrets，确保 DB_URL 已配置")

    # 注入环境变量
    os.environ["GOOGLE_API_KEY"] = google_key
    os.environ["GAODE_API_KEY"] = gaode_key
    os.environ["TOMORROW_API_KEY"] = tomorrow_key

    model = Gemini(id="gemini-2.5-flash")
    
    # 🔴 关键变化 4：创建 Postgres 数据库连接
    # 这里真正使用了 db_url 变量！
    db = PostgresDb(
        db_url=db_url,
        session_table="agent_sessions"  # 自定义表名
    )

    # 创建 Agent
    agent = Agent(
        model=model,
        session_id=session_id,
        db=db, # 🔴 关键变化 5：传入 Postgres 实例
        add_history_to_context=True,
        tools=[GaodeToolkit(), TomorrowWeatherToolkit()],
        markdown=True,
        debug_mode=True, 
        description="你是一位拥有10年经验的高级私人旅行定制师...",
        instructions=[
            "1. 必须确认：几人出行？有无老人小孩？偏好风格？",
            "2. 必须用 `hourly_weather` 查天气，用 `search_places` 查地点。",
            "3. 方案包含：👔衣、🥣食、🏠住/玩、🚗行。",
            "4. 如果用户之前提供过信息，不要重复问。"
        ]
    )
    return agent

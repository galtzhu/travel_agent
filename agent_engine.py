import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
# 导入 OpenAIChat
from agno.models.openai import OpenAIChat
from agno.db.postgres import PostgresDb
from tools.gaode_tool import GaodeToolkit
from tools.tomorrow_weather_tool import TomorrowWeatherToolkit

load_dotenv()

# 🔴 关键修复：定义一个兼容 Qwen 的模型类
# 继承 OpenAIChat，强行把 system_message_role 改回 "system"
class QwenChat(OpenAIChat):
    @property
    def system_message_role(self) -> str:
        return "system"

def get_env_var(key_name):
    try:
        return st.secrets[key_name]
    except (FileNotFoundError, KeyError):
        return os.getenv(key_name)

def get_travel_agent(session_id="default_session"):
    # 1. 读取 Key
    qwen_key = get_env_var("DASHSCOPE_API_KEY") 
    gaode_key = get_env_var("GAODE_API_KEY")
    tomorrow_key = get_env_var("TOMORROW_API_KEY")
    db_url = get_env_var("DB_URL")

    # 2. 检查 Key
    if not all([qwen_key, gaode_key, tomorrow_key, db_url]):
        raise ValueError("密钥缺失！请检查 .env 或 Streamlit Secrets")

    # 3. 注入环境变量
    os.environ["GAODE_API_KEY"] = gaode_key
    os.environ["TOMORROW_API_KEY"] = tomorrow_key

    # 🔴 关键修复：使用我们自定义的 QwenChat 类
    model = QwenChat(
        id="qwen-plus", 
        api_key=qwen_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    # 4. 数据库连接
    db = PostgresDb(
        db_url=db_url,
        session_table="agent_sessions"
    )

    # 5. 创建 Agent
    agent = Agent(
        model=model, # 这里用兼容版模型
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

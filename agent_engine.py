import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
# 导入数据库模块
from agno.db.sqlite import SqliteDb
# 导入你的工具
from tools.gaode_tool import GaodeToolkit
from tools.tomorrow_weather_tool import TomorrowWeatherToolkit

load_dotenv()

# 定义数据库文件路径
DB_PATH = "agent_storage.db"

def get_travel_agent(session_id="default_session"):
    # 1. 检查 Key
    if not os.getenv("GAODE_API_KEY") or not os.getenv("TOMORROW_API_KEY"):
        raise ValueError("请先配置 GAODE_API_KEY 和 TOMORROW_API_KEY")

    # 2. 初始化模型
    model = Gemini(id="gemini-2.5-flash")
    
    # 3. 初始化数据库连接
    # 文档截图显示直接传入 db_file
    db = SqliteDb(db_file=DB_PATH)

    # 4. 创建 Agent
    agent = Agent(
        model=model,
        session_id=session_id,
        
        # 🟢 修正点 1：参数名改为 db
        db=db,
        
        # 🟢 修正点 2：参数名改为 add_history_to_context
        # 这会让 Agent 自动读取数据库里的历史记录，作为上下文发给 Gemini
        add_history_to_context=True,
        
        # 🟢 修正点 3：删除了 num_history_responses (避免报错)
        
        tools=[GaodeToolkit(), TomorrowWeatherToolkit()],
        markdown=True,
        debug_mode=True, 
        description="你是一位拥有10年经验的高级私人旅行定制师...",
        instructions=[
            "1. 优先检查对话历史，不要重复询问已知信息。",
            "2. 必须调用 `hourly_weather` 查天气。",
            "3. 必须调用 `search_places` 查真实地点。",
            "4. 输出包含：👔衣、🥣食、🏠住/玩、🚗行 四个维度。"
        ]
    )
    return agent

import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini

# 导入两个工具
from tools.gaode_tool import GaodeToolkit
from tools.tomorrow_weather_tool import TomorrowWeatherToolkit

load_dotenv()

# 1. 检查所有 Key
if not os.getenv("GAODE_API_KEY") or not os.getenv("TOMORROW_API_KEY"):
    print("⚠️  警告: 请检查 .env 文件，确保 GAODE_API_KEY 和 TOMORROW_API_KEY 都已配置")

# 2. 初始化模型
model = Gemini(id="gemini-2.5-flash")

# 3. 创建全能 Agent
agent = Agent(
    model=model,
    # 🌟 双剑合璧：同时加载地图和天气工具
    tools=[GaodeToolkit(), TomorrowWeatherToolkit()],
    markdown=True,
    debug_mode=True,
    description="你是一个全能的旅行助手。你可以查询实时地点信息，也可以查询精准的小时级天气。",
    instructions=[
        "1. 如果用户问地点，使用 gaode_map 工具。",
        "2. 如果用户问天气，使用 hourly_weather 工具。",
        "3. 如果用户的问题涉及'安排行程'（例如：明天下午去逛街），请先查询天气，再根据天气情况推荐适合的地点（室内/室外）。",
        "4. 回答要贴心，比如降水概率超过 30% 就要提醒带伞。"
    ]
)

# 4. 终极测试
print("🤖 全能旅行助手启动...")

# 测试场景：这是一个复杂的复合指令，考验 Agent 能否同时调用两个工具并进行逻辑推理
query = "我计划明天下午 2 点在北京朝阳区逛逛，那时候天气怎么样？适合去室外公园还是找个商场？请推荐具体地点。"

agent.print_response(query, stream=True)
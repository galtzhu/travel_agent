import os
import requests
import json
from agno.tools import Toolkit


class TomorrowWeatherToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="hourly_weather")
        self.register(self.get_hourly_weather)

    def get_hourly_weather(self, location: str) -> str:
        """
        获取指定地点的未来 12 小时逐小时天气预报。
        包含温度、降水概率、天气状况等。

        Args:
            location (str): 城市名称，例如 "Beijing", "Shanghai", "Tokyo" (最好用拼音或英文，中文也支持但有时不稳定)

        Returns:
            str: 格式化后的天气数据
        """
        api_key = os.getenv("TOMORROW_API_KEY")
        if not api_key:
            return "错误：未配置 TOMORROW_API_KEY"

        # Tomorrow.io 的 API 端点
        url = "https://api.tomorrow.io/v4/weather/forecast"

        params = {
            "location": location,
            "apikey": api_key,
            "timesteps": "1h",  # 只要小时级数据
            "units": "metric"  # 公制单位 (摄氏度)
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            # 错误处理
            if "timelines" not in data:
                return f"天气查询失败: {data.get('message', '未知错误')}"

            # --- 数据清洗核心逻辑 ---
            # 我们只取未来 12 个小时的数据，给 Agent 减负
            hourly_data = data["timelines"]["hourly"][:12]

            summary = []
            for hour in hourly_data:
                time_str = hour["time"].split("T")[1][:5]  # 提取 "14:00" 格式
                values = hour["values"]

                # 提取关键指标
                temp = values.get("temperature", "N/A")
                rain_chance = values.get("precipitationProbability", 0)
                condition_code = values.get("weatherCode", 0)

                # 简单翻译几个常见的天气代码 (可选，Agent 其实能读懂数字代码，但文字更直观)
                # 这里只做简单拼接，依靠 Agent 的理解能力
                summary.append(
                    f"⏰{time_str} | 🌡️{temp}°C | ☔降水概率:{rain_chance}%"
                )

            # 将列表合并成一个字符串返回
            return "\n".join(summary)

        except Exception as e:
            return f"天气工具出错: {e}"
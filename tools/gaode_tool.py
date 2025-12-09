import os
import requests
import json
from agno.tools import Toolkit


class GaodeToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="gaode_map")
        # 注册工具功能：告诉 Agent 我有 search_places 这个技能
        self.register(self.search_places)

    def search_places(self, keyword: str, city: str = None) -> str:
        """
        在高德地图上搜索地点。

        Args:
            keyword (str): 搜索关键词。
            city (str): 城市名称。
            注意：如果用户没有明确说明城市（例如只说了"附近"），请尝试从之前的对话历史中推断城市。
            如果无法推断，请将此参数留空，不要编造。
        """
        # 如果 LLM 真的没传 city，且无法推断，工具内部进行防御
        if not city:
            return "错误：缺失城市信息。请提示 Agent 询问用户当前所在的城市。"
        api_key = os.getenv("GAODE_API_KEY")
        if not api_key:
            return "错误：未配置 GAODE_API_KEY"

        url = "https://restapi.amap.com/v5/place/text"
        params = {
            "key": api_key,
            "keywords": keyword,
            "city": city,
            "show_fields": "business,photos",  # 返回更多细节
            "page_size": 5  # 只看前5个，节省token
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] != "1":
                return f"高德API调用失败: {data.get('info')}"

            # 简化返回数据，只提取关键信息给 LLM，节省 Token
            results = []
            for poi in data.get("pois", []):
                results.append({
                    "名称": poi.get("name"),
                    "地址": poi.get("address"),
                    "类型": poi.get("type"),
                    "评分": poi.get("biz_ext", {}).get("rating", "暂无"),
                    "人均": poi.get("biz_ext", {}).get("cost", "暂无")
                })

            return json.dumps(results, ensure_ascii=False)

        except Exception as e:
            return f"查询出错: {e}"


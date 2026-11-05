from dotenv import load_dotenv
from openai import OpenAI

from agent_day04 import FinancialReport
import os

class FinancialExtractor:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key= os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_BASE_URL"])
        self.model = model=os.environ["OPENAI_MODEL"]

    def extract(self, text: str) -> FinancialReport:
        response = self.client.responses.parse(model=self.model, instructions=(
            "你是一名财务数据提取助手。"
            "只提取用户提供的财务数据。"
            "不得自行编造数字。"
            "如果必要字段缺失，不要猜测。"
        ), input=text, text_format=FinancialReport,)

        if response.status != "completed":
            raise RuntimeError(f"响应未完成: {response.status}")

        ###这里使用的是 Python SDK 的 responses.parse() 辅助方法。
        ###它能够根据 Pydantic 模型生成受支持的结构化输出 Schema，并尝试将响应解析为指定类型。
        result = response.output_parsed

        if result is None:
            raise ValueError("模型没有返回可解析的财务数据")

        return result

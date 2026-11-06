import os

from dotenv import load_dotenv
from openai import OpenAI

from agent_day05.stock_tools import execute_tool
from agent_day05.tool_definitions import TOOLS


class StockAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_BASE_URL"])
        self.model = os.environ["OPENAI_MODEL"]

    def run(self, question: str) -> str:
        response = self.client.responses.create(model=self.model, instructions=(
            "你是一名股票数据查询助手。"
            "需要股票数据时必须使用工具。"
            "工具中的数据均为模拟数据，"
            "不得将其描述为真实或实时行情。"), input=question, tools=TOOLS)

        if response.status != "completed":
            raise RuntimeError(f"模型响应未完成: {response.status}")
        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            return response.output_text
        tool_outputs = []

        for call in tool_calls:
            result = execute_tool(call.name, arguments=call.arguments)
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result,
            })

        final_response = self.client.responses.create(
            model=self.model,
            instructions=(
                "根据工具结果回答用户问题。"
                "所有数据都是模拟数据，"
                "必须明确说明不是实时行情。"
            ),
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
            tool_choice="none",
        )

        if final_response.status != "completed":
            raise RuntimeError(
                f"最终响应未完成：{final_response.status}"
            )

        return final_response.output_text
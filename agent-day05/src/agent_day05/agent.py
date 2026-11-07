import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from agent_day05.stock_tools import execute_tool
from agent_day05.tool_definitions import TOOLS

INSTRUCTIONS = """
你是一名股票研究助手。

规则：
1. 查询股票数据时必须使用工具。
2. 所有股票数据均为虚构的模拟数据。
3. 不得将模拟数据描述为真实行情。
4. 不得编造工具没有提供的数据。
5. 工具发生错误时，可以尝试合理恢复。
6. 如果任务无法完成，应明确说明原因。
7. 能够回答时直接回答，不要重复调用工具。
"""

class StockAgent:
    def __init__(self, max_steps: int = 5, max_tool_calls: int = 10, max_seconds: float = 60.0):
        load_dotenv()
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_BASE_URL"])
        self.model = os.environ["OPENAI_MODEL"]

        if max_steps < 1 or max_tool_calls < 1 or max_seconds <= 0 :
            raise ValueError("执行限制必须为正数")

        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.max_seconds = max_seconds

    def run(self, question: str) -> str:
        response_id = None
        pending_input = question
        total_tool_calls = 0
        started_at = time.monotonic()

        for step in range(1, self.max_steps + 1):
            if time.monotonic() - started_at >= self.max_seconds:
                return "Agent 以已经达到执行时间限制"

            print(f"\n[Agent Step {step}]")
            request = {"model": self.model,
                       "instructions": INSTRUCTIONS,
                       "input": pending_input,
                       "tools": TOOLS,
                       "tool_choice" : "auto"
                       }
            if response_id is not None:
                request["previous_response_id"] = response_id
            response = self.client.responses.create(**request)
            tool_calls = [item for item in response.output if item.type == "function_call"]

            # 没有工具调用，说明模型已经给出最终答案
            if not tool_calls:
                return response.output_text or "没有返回文本回答"
            if total_tool_calls + len(tool_calls) > self.max_tool_calls:
                return "Agent 已达到工具调用次数限制。"

            tool_outputs = []
            for call in tool_calls:
                print(f"[Tool] {call.name}")
                print(f"[Args] {call.arguments}")
                result = execute_tool(name = call.name, arguments = call.arguments)
                print(f"[Result {result}]")

                tool_outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": result})
                total_tool_calls += 1

            response_id = response.id
            pending_input = tool_outputs

        return "Agent 已经达到最大执行轮数，任务未能完成"

    #需要注意：max_seconds 在这里是轮次之间检查的软时间限制，不是强制中断计时器。如果单次网络请求阻塞，实际总耗时仍可能超过设定值。生产环境还需要端到端超时、取消机制和费用预算。




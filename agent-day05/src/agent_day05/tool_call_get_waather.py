import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_BASE_URL"])

def get_weather(location):
    """模拟查询天气的本地API"""
    print(f"\n[本地执行] 正在查询 {location} 的天气...")
    # 真实场景中，这里会发起 HTTP 请求调用气象局 API
    return json.dumps({"location": location, "temperature": "22℃", "condition": "多云"})

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气情况",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称，例如：北京，上海"
                }
            },
            "required": ["location"]
        }
    }
}]

# 对话历史上下文
messages = [{"role": "user", "content": "今天杭州天气怎么样？"}]
print("[步骤1] 向大模型发送带有 tools 的提问...")
response = client.chat.completions.create(
    model=os.environ["OPENAI_MODEL"],
    messages=messages,
    tools=tools,
    tool_choice="auto" # 让模型自己决定是否调用工具
)

message = response.choices[0].message
messages.append(message) # 将模型的回复（包含调用指令）加入对话历史

if message.tool_calls:
    for tool_call in message.tool_calls:
        # ==========================================
        # 2. 应用程序本地执行 (Execution)
        # ==========================================
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"[步骤2] 模型请求调用工具: {function_name}, 参数: {function_args}")

        # 路由到对应的本地函数
        if function_name == "get_weather":
            function_response = get_weather(
                location=function_args.get("location")
            )

            # ==========================================
            # 3. 结果回传大模型 (Result Return)
            # ==========================================
            print(f"[步骤3] 本地函数执行完毕，准备回传结果: {function_response}")
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

    # ==========================================
    # 4. 最终总结 (Final Response)
    # ==========================================
    print("\n[步骤4] 将执行结果发回给大模型，等待最终总结...")
    second_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    print("\n大模型的最终回复：")
    print(second_response.choices[0].message.content)
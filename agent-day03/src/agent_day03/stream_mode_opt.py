import os

from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIConnectionError, APIError

load_dotenv()
#timeout=30.0：限制网络操作等待时间
client = OpenAI(api_key= os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_BASE_URL"],
                timeout=30.0)
#completed：单独记录是否收到成功完成事件。
completed = False
#parts：增量拼接完整文本，供后续 Agent 处理。
parts=[]
## with：结束迭代或发生异常时释放连接。
try:
    with client.responses.create(
        model=os.environ["OPENAI_MODEL"],
        input="请解释 Transformer 的工作原理",
        stream=True,
    ) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
                parts.append(event.delta)
            elif event.type == "response.completed":
                completed = True
                print("\n生成完成")
                break
            # response.failed / response.incomplete：识别非正常结束。
            elif event.type in ("response.failed", "response.incomplete", "error"):
                print(f"\n生成异常: {event}")
                break
except APITimeoutError:
    print("\n读取超时")
except APIConnectionError as e:
    print(f"\n网络连接异常: {e}")
except APIError as e:
    print(f"\nAPI 错误: {e}")
finally:
    if not completed:
        print("\n本次响应未正常完成")
full_text = "".join(parts)
print(f"已接收文本长度：{len(full_text)}")
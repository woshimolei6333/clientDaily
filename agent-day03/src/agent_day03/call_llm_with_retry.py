import os
import random
import time

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_BASE_URL"],
                timeout=30.0,
                max_retries=2)
def call_llm_with_retry(prompt: str, max_retries=3):
    for attempt in range(max_retries + 1):
        try:
            response = client.responses.create( model=os.environ["OPENAI_MODEL"], input= prompt)
            return response.output_text
        except (openai.APITimeoutError, openai.APIConnectionError, openai.RateLimitError, openai.InternalServerError) as e:
            print(f"第 {attempt + 1} 次请求失败: {e}")

            if attempt == max_retries:
                raise
            delay = min(2 ** attempt, 30)
            delay += random.uniform(0, 1)
            print(f"等待 {delay:.2f} 秒重试")
            time.sleep(delay)

        except openai.APIStatusError as e:
            if e.status_code not in (408, 409):
                raise

            if attempt == max_retries:
                raise

            delay = min(2 ** attempt, 30)
            delay += random.uniform(0, 1)
            time.sleep(delay)
    return None


if __name__ == "__main__":
    result = call_llm_with_retry(
        "用100字介绍什么是 AI Agent"
    )
    print(result)
import os
from multiprocessing.context import AuthenticationError

from openai import OpenAI, BadRequestError, RateLimitError, APITimeoutError, \
    APIConnectionError, InternalServerError, OpenAIError

#这里保留 SDK 内置的两次重试，不再额外实现手动重试循环。
#重试需要谨慎,假设一次模型请求已经在服务器完成，但客户端因为网络中断没有收到响应。
class LLMClientDemo:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"],
                             base_url=os.environ["OPENAI_BASE_URL"],
                             timeout=30.0,
                             max_retries=2)
        self.model = os.environ["OPENAI_MODEL"]

    def generate(self, prompt) -> str:
        try:
            response = self.client.responses.create(model = self.model, input = prompt)
            if response.status != "completed":
                raise RuntimeError(f"模型未正常完成: {response.status}")
            return response.output_text
        except AuthenticationError:
            raise RuntimeError("API Key 无效，请检查配置")
        except BadRequestError as error:
            raise RuntimeError(f"请求参数错误: {error}") from error
        except RateLimitError:
            raise RuntimeError("请求受到限制，请检查限流或账户额度")
        except APITimeoutError:
            raise RuntimeError("LLM 请求超时")
        except APIConnectionError:
            raise RuntimeError("无法连接 LLM 服务")
        except InternalServerError:
            raise RuntimeError("LLM 服务端错误")
        except OpenAIError as error:
            raise RuntimeError(
                f"LLM API 调用失败: {error}"
            ) from error

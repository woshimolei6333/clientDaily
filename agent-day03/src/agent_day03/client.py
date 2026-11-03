import logging
import time
from typing import TypeVar
import random
from openai import OpenAI, APIConnectionError, APITimeoutError, APIStatusError, BadRequestError
from collections.abc import Callable, Iterator
from agent_day03.config import LLMConfig

logger = logging.getLogger(__name__)
T = TypeVar("T")

class LLMError(Exception):
    """统一的 LLM 调用异常。"""

class LLMClient:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()

        self.client = OpenAI(api_key=self.config.api_key,
                             base_url=self.config.base_url,
                             timeout=self.config.timeout,
                             max_retries=0
                             )

    def _retryable(self, error: Exception) -> bool:
        if isinstance(error, (APIConnectionError, APITimeoutError)):
            return True

        if isinstance(error, APIStatusError):
            return error.status_code in (408, 409, 429, 500, 502, 503, 504)
        return False

    def _request_with_retry(
            self, operation: Callable[[], T]
    ) -> T:
        for attempt in range(self.config.max_retries + 1):
            from openai import AuthenticationError
            try:
                return operation()
            except (AuthenticationError, BadRequestError):
                # "配置、权限或请求参数问题，重试通常无效"#
                raise
            except (APIConnectionError, APITimeoutError, APIStatusError) as error:
                if not self._retryable(error) or attempt >= self.config.max_retries:
                    raise

                maximum = min(2 ** attempt, 30)
                delay = random.uniform(0, maximum)
                logger.warning("LLM请求失败: %s; %.2f秒后重试 (%d/%d)", type(error).__name__, delay, attempt + 1,
                               self.config.max_retries)
                time.sleep(delay)
        raise RuntimeError("不可达的重试状态")

    def chat(self, message: str, instructions: str = "你是一名专业的AI助手") -> str:
        response = self._request_with_retry(lambda: self.client.responses.create(model=self.config.model,
                                                                                 instructions=instructions,
                                                                                 input=message))
        if response.status != "completed":
            raise LLMError(f"模型没有正常完成: {response.status}")
        return response.output_text

    def stream(self, message: str, instructions: str = "你是一名专业的AI助手") -> Iterator[str]:
        """流动式调用:逐段返回文本"""

        def operation():
            return self.client.responses.create(model=self.config.model, instructions=instructions, input=message,
                                                stream=True)
        events = self._request_with_retry(operation)
        completed = False
        try:
            for event in events:
                # response.output_text.delta 表示文本增量
                if event.type == "response.output_text.delta":
                    delta = event.delta
                    if not isinstance(delta, str):
                        raise LLMError(
                            f"预期字符串增量，实际收到: {type(delta).__name__}"
                        )
                    yield delta

                elif event.type == "response.completed":
                    completed = True

                elif event.type in (
                        "response.failed",
                        "response.incomplete",
                        "error",
                ):
                    raise LLMError(
                        f"流式生成失败: {event.type}"
                    )

            if not completed:
                raise LLMError(
                    "流式连接结束，但未收到response.completed"
                )
        finally:
            events.close()

    def close(self):
        """释放底层 HTTP 连接资源。"""
        self.client.close()
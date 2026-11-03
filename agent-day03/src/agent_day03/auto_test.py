
# tests/test_client.py

from unittest.mock import patch
from openai import APIConnectionError

from agent_day03.client import LLMClient
from agent_day03.config import LLMConfig
def test_retry_on_connection_error():
    config = LLMConfig(
        api_key="test-key",
        model="test-model",
        max_retries=3,
    )


    llm = LLMClient(config)
    attempts = 0

    def fake_operation():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise APIConnectionError(
                request=None  # 测试中模拟网络错误
            )

        return "success"

    try:
        with patch("agent_day03.client.time.sleep"):
            result = llm._request_with_retry(
                fake_operation
            )

        assert result == "success"
        assert attempts == 3
    finally:
        llm.close()

if __name__ == '__main__':
    test_retry_on_connection_error()
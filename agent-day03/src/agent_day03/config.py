import os
from dataclasses import dataclass

#@dataclass：自动生成初始化方法，适合存放配置。
#frozen=True 配置对象创建后不能直接修改字段
#@classmethod：通过 LLMConfig.from_env() 创建配置对象。


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    model: str
    base_url: str | None = None
    timeout: float = 30.0
    max_retries: int = 3

    # -> 是 Python 的返回值类型注解
    # 接引用这个尚未完成定义的类名可能出现问题，"LLMConfig" 把类型名称作为前向引用（Forward Reference），避免立即解析它
    @classmethod
    def from_env(cls) -> "LLMConfig":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL")
        base_url = os.getenv("OPENAI_BASE_URL")
        if not api_key:
            raise ValueError("缺少 OPENAI_API_KEY")
        if not model:
            raise ValueError("缺少 OPENAI_MODEL")

        timeout = float(os.getenv("LLM_TIMEOUT", "30"))
        retries = int(os.getenv("LLM_MAX_RETRIES", "3"))

        if timeout <= 0 or retries < 0:
            raise ValueError("超时必须大于0，重试次数不能小于0")

        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url or None,
            timeout=timeout,
            max_retries=retries,
        )

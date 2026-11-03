# agent-day03：LLM 调用、重试与流式响应练习

这是一个基于 Python 3.12 和 OpenAI Python SDK 的练习项目。代码从最简单的 Responses API 调用开始，逐步加入环境配置、错误分类、指数退避重试、流式事件处理和可复用的 `LLMClient`。

## 学习路线

1. 阅读 `main.py`，理解一次普通请求：创建客户端、传入 `model` / `instructions` / `input`，读取 `response.output_text`。
2. 阅读 `stream_demo.py` 和 `stream_mode_opt.py`，理解 `stream=True`、文本增量事件与完成事件。
3. 阅读 `llm_client.py` 和 `call_llm_with_retry.py`，比较 SDK 内置重试和手写重试。
4. 阅读 `config.py`、`client.py`、`test_client.py` 和 `auto_test.py`，理解如何把配置、调用、资源释放与测试组织成可复用代码。

## 项目文件与对应知识

| 文件 | 作用 | 对应知识点 |
| --- | --- | --- |
| `README.md` | 项目说明与学习索引 | 把示例、配置和已知限制放在同一入口。 |
| `pyproject.toml` | 声明 Python 版本、依赖、构建后端和命令行入口 | Python 项目元数据、依赖声明、`uv_build`；当前入口 `agent_day03:main` 尚无对应的 `main` 函数，见下文。 |
| `uv.lock` | 锁定解析后的依赖版本 | 可重复安装；通常与 `pyproject.toml` 一起保留。 |
| `.python-version` | 指定 Python 3.12 | 本地 Python 版本选择。 |
| `.gitignore` | 忽略 Python 构建产物和 `.venv` | 版本控制卫生；目前没有忽略 `.env`。 |
| `.env` | 本地 API 地址、密钥、模型等配置 | 环境变量与密钥管理；不要把真实密钥提交到仓库。本文不展示其内容。 |
| `src/agent_day03/__init__.py` | 加载 `.env`，创建客户端，并在包导入时调用模型 | Python 包初始化与导入副作用：**导入 `agent_day03` 就会发起网络请求**，当前也没有定义 `main()`。 |
| `src/agent_day03/main.py` | 最小普通请求示例 | `load_dotenv()`、`OpenAI`、Responses API、`instructions`、`output_text`。 |
| `src/agent_day03/stream_demo.py` | 最小流式输出示例 | `stream=True`、遍历事件、`response.output_text.delta`、实时打印。 |
| `src/agent_day03/stream_mode_opt.py` | 增强的流式示例 | 超时、连接/API 异常、`response.completed` 判定、异常结束事件、拼接文本、上下文管理器释放流。 |
| `src/agent_day03/llm_client.py` | 使用 SDK 内置重试的封装示例 | 异常分类、`max_retries=2`、请求状态检查；其中 `AuthenticationError` 来自 `multiprocessing.context`，并非 OpenAI SDK，应先修正再使用。 |
| `src/agent_day03/call_llm_with_retry.py` | 手动重试的独立示例 | 可重试错误、指数退避、随机抖动、最大等待时间；它同时设置 SDK 的 `max_retries=2`，一次外层尝试内部还可能重试。 |
| `src/agent_day03/config.py` | `LLMConfig` 不可变配置及 `from_env()` | `@dataclass(frozen=True)`、类方法、类型注解、环境变量读取与参数校验。 |
| `src/agent_day03/client.py` | 可复用的 `LLMClient` | 统一普通/流式调用、可重试状态码、全抖动退避、禁用 SDK 内置重试以避免叠加、`LLMError`、连接与流的关闭。 |
| `src/agent_day03/test_client.py` | `LLMClient.stream()` 的手动运行示例 | 逐块消费流、异常捕获、`finally` 释放客户端；尽管文件名含 `test`，它不是自动化断言测试。 |
| `src/agent_day03/auto_test.py` | 模拟连接失败两次、第三次成功的测试函数 | `unittest.mock.patch`、验证重试次数和返回值；当前放在源码目录，可直接作为脚本运行，但导入包会触发 `__init__.py` 的请求。 |

生成目录：`.venv/` 是本地虚拟环境，`src/agent_day03/__pycache__/` 是 Python 字节码缓存，`.idea/` 是编辑器配置。它们不是本项目的教学源码，无需逐个阅读其中的依赖或缓存文件。

## 核心知识串联

### 配置与一次请求

普通请求使用 `client.responses.create(...)`，把提示词放在 `input`，把角色要求放在 `instructions`，再通过 `response.output_text` 获取文本。`config.py` 从 `OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_BASE_URL`、`LLM_TIMEOUT` 和 `LLM_MAX_RETRIES` 读取配置，并校验必填项及数值范围。`OPENAI_BASE_URL` 用于指定兼容 OpenAI API 的服务地址；是否支持 Responses API 取决于所连接服务。

`main.py` 等独立示例调用 `load_dotenv()`；`LLMConfig.from_env()` 本身只读取当前进程环境变量。当前 `__init__.py` 虽然也调用 `load_dotenv()`，但随之立即发请求，因此通过导入包来加载 `.env` 会产生意外网络调用。

### 错误与重试

连接失败、超时、限流和部分服务端状态通常适合有限次数的重试；认证失败和错误请求通常需要先修正配置或参数。`client.py` 对连接/超时异常及 HTTP 408、409、429、500、502、503、504 重试，使用指数增长的等待上限和随机抖动，并把 SDK 的内置重试设为 0。`call_llm_with_retry.py` 则展示另一种写法：固定指数退避加随机抖动，但其 SDK 内置重试仍开启。网络中断后，服务端可能已完成请求，重复调用可能带来重复消耗。

### 流式响应

流式调用返回事件迭代器：`response.output_text.delta` 携带文本片段，`response.completed` 表示正常完成，`response.failed` / `response.incomplete` / `error` 表示异常结束。`client.py` 的 `stream()` 使用生成器逐段返回文本，并在 `finally` 中关闭流。它的重试只包住**建立流**的步骤；流已经开始后若读取中断，不会自动从中间恢复。

## 运行方式

在项目根目录执行：

```bash
uv sync
uv run python src/agent_day03/main.py
uv run python src/agent_day03/stream_demo.py
uv run python src/agent_day03/stream_mode_opt.py
uv run python src/agent_day03/call_llm_with_retry.py
```

运行前准备 `OPENAI_API_KEY` 和 `OPENAI_MODEL`；使用自定义服务时还需正确设置 `OPENAI_BASE_URL`。这些独立脚本会加载项目根目录的 `.env`。请避免将真实密钥写入代码或提交到仓库。

当前不建议直接运行 `uv run agent-day03`：`pyproject.toml` 指向 `agent_day03:main`，而包没有导出 `main` 函数。`test_client.py`、`auto_test.py` 或其他导入 `agent_day03` 的代码，也会先执行 `__init__.py` 中的模型请求。若要把这些文件作为稳定的测试或命令行入口使用，应先把示例请求从 `__init__.py` 移出，再补上真正的入口函数。

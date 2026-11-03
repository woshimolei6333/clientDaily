import logging

from agent_day03.client import LLMClient, LLMError

logging.basicConfig(level=logging.INFO)

def main():
    llm = LLMClient()
    try:
        print("===普通调用===")
        for chunk in llm.stream("解释Transformer中的注意力机制"):
            print(chunk, end = "", flush=True)
        print()

    except LLMError as error:
        print(f"模型生成异常: {error}")

    except Exception as error:
        print(f"请求异常: {type(error).__name__}: {error}")

    finally:
        llm.close()

if __name__ == "__main__":
    main()
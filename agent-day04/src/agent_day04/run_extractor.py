from dotenv import load_dotenv
from agent_day04.extractor import FinancialExtractor

load_dotenv()


def main():
    # 模拟一段财报文本
    text = """
    苹果公司（AAPL）2025财年财务报告：
    营业收入为4162亿美元，
    净利润为1120亿美元，
    营收同比增长6.4%。
    """

    extractor = FinancialExtractor()

    try:
        result = extractor.extract(text)

        print("✅ 提取成功！")
        print(result.model_dump_json(indent=2))

    except Exception as e:
        print(f"❌ 提取失败: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
import argparse

from dotenv import load_dotenv

from agent_day04.extractor import FinancialExtractor


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="股票财务数据提取器")
    parser.add_argument(
        "--text",
        required=True,
        help="待提取的财务文本",
    )
    args = parser.parse_args()

    extractor = FinancialExtractor()
    try:
        report = extractor.extract(args.text)
        print("===结构化财务数据====")
        print(report.model_dump_json(indent=2))
        growth = report.revenue_growth()

        if growth is None:
            print("营收同比增长率：无法统计")
        else:
            print(f"营收同比增长率：{growth:.2f}%")
    except Exception as error:
        print(f"提取失败:{error}")
        raise SystemExit(1)
if __name__ == '__main__':
    main()
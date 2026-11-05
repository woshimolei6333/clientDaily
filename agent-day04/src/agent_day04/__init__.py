from agent_day04.model import FinancialReport


def main() -> None:
    report = FinancialReport(ticker="NVDA", revenue=30, previous_revenue = 200,
                             net_income=150, currency="USD", unit = "亿")
    print(report.revenue)
    print(report.model_dump())
    print(report.model_dump_json(indent=2))
    new_report = FinancialReport.model_validate_json(
        '{"ticker":"NVDA","revenue":300,'
        '"previous_revenue":200,"net_income":150,'
        '"currency":"USD","unit":"亿"}'
    )

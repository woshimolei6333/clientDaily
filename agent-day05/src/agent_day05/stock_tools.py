import json

from pydantic import BaseModel, ConfigDict, Field


class StockArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, maxLength=10)


MOCK_STOCKS = {
    "NVDA": {
        "price": 150.5,
        "revenue": 300.0,
        "net_income": 150.0,
    },
    "AMD": {
        "price": 180.2,
        "revenue": 75.0,
        "net_income": 12.0,
    },
}

def get_stock_price(ticker: str) -> dict:
    ticker = ticker.upper()

    if ticker not in MOCK_STOCKS:
        return {
            "error": f"不支持的股票代码：{ticker}"
        }

    return {
        "ticker": ticker,
        "price": MOCK_STOCKS[ticker]["price"],
        "currency": "USD",
        "is_mock": True,
    }

def get_financial_report(ticker: str) -> dict:
    ticker = ticker.upper()

    if ticker not in MOCK_STOCKS:
        return {
            "error": f"不支持的股票代码：{ticker}"
        }

    return {
        "ticker": ticker,
        "revenue": MOCK_STOCKS[ticker]["revenue"],
        "net_income": MOCK_STOCKS[ticker]["net_income"],
        "currency": "USD",
        "unit": "亿美元",
        "is_mock": True,
    }

TOOL_REGISTRY = {
    "get_stock_price": get_stock_price,
    "get_financial_report": get_financial_report,
}
def execute_tool(
    name: str,
    arguments: str,
) -> str:
    if name not in TOOL_REGISTRY:
        return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
    try:
        args = StockArgs.model_validate_json(arguments)
        result = TOOL_REGISTRY[name](ticker = args.ticker)
        return json.dumps(result, ensure_ascii=False)
    except Exception as error:
        return json.dumps({
            "error": str(error)
        }, ensure_ascii=False)
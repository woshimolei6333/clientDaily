import datetime
import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from agent_day05.difference_args import DifferenceArgs
import yfinance as yf

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

def calculate_difference(a: float, b: float) -> dict:
    return {
        "a": a,
        "b": b,
        "difference": round(a - b, 4)
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



def get_real_stock_price(ticker: str) -> dict:
    ticker = ticker.strip().upper()
    if not ticker:
        return ValueError("股票代码不能为空")

    stock_prick = yf.Ticker(ticker)
    history = stock_prick.history(period="5d",
        interval="5m",
        auto_adjust=False,
        prepost=False,
        timeout=10,
        raise_errors=True,)
    if history.empty:
        raise ValueError(f"未获取到 {ticker} 的行情")
    latest = history.iloc[-1]
    from time import timezone
    return {
        "ticker": ticker,
        "price": float(latest["Close"]),
        "open": float(latest["Open"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"]),
        "volume": int(latest["Volume"]),
        "bar_time": history.index[-1].isoformat(),
        "retrieved_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "interval": "5m",
        "source": "Yahoo Finance",
    }

TOOL_REGISTRY = {
    "get_stock_price": get_stock_price,
    "get_financial_report": get_financial_report,
    "calculate_difference": calculate_difference
}
def execute_tool(
    name: str,
    arguments: str,
) -> str:
    func = TOOL_REGISTRY.get(name)
    if func is None:
        return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
    try:
        if name == "calculate_difference":
            args = DifferenceArgs.model_validate_json(arguments)
        else :
            args = StockArgs.model_validate_json(arguments)
        result = func(**args.model_dump())
        return json.dumps(result, ensure_ascii=False)

    except ValidationError as error:
        return json.dumps({
            "error": "invalid_arguments",
            "message": str(error),
        }, ensure_ascii=False)

    except Exception as error:
        return json.dumps({
            "error": "tool_execution_failed",
            "message": "工具执行失败",
        }, ensure_ascii=False)

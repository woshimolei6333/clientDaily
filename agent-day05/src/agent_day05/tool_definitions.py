TOOLS = [{
    "type": "function",
    "name": "get_stock_price",
    "description": "查询指定股票的模拟价格数据。",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "股票代码，例如 NVDA、AMD"
            }
        },
        "required": ["ticker"],
        "additionalProperties": False
    },
    "strict": True
}, {
    "type": "function",
    "name": "get_financial_report",
    "description": "查询指定股票的模拟财务数据。",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "股票代码，例如 NVDA、AMD"
            }
        },
        "required": ["ticker"],
        "additionalProperties": False
    },
    "strict": True
}]

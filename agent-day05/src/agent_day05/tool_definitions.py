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
}, {
    "type": "function",
    "name": "calculate_difference",
    "description": "计算两个数字的差额 a-b，适合比较股票价格等数值。",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "被减数"
            },
            "b": {
                "type": "number",
                "description": "减数"
            }
        },
        "required": ["a", "b"],
        "additionalProperties": False
    },
    "strict": True
}]

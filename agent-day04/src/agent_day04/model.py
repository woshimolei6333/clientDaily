from pydantic import ConfigDict, BaseModel, Field, model_validator


class FinancialReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1)
    # 表示字段必须存在，但值允许为 None
    revenue: float | None
    previous_revenue: float | None
    net_income: float | None
    currency: str | None
    unit: str | None

    # 使用@model_validator 它可以在模型解析完成后执行跨字段或业务规则校验
    @model_validator(mode="after")
    def validate_financial_data(self):
        if self.revenue is not None and self.revenue < 0:
            raise ValueError("盈收不能为负数")
        if self.previous_revenue is not None and self.previous_revenue < 0:
            raise ValueError("去年同期营收也不能为负数")
        return self

    def revenue_growth(self) -> float | None:
        if self.revenue is None or self.previous_revenue is None or self.previous_revenue == 0:
            return None
        return (self.revenue - self.previous_revenue) / self.previous_revenue * 100

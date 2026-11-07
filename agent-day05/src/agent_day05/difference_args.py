from pydantic import BaseModel, ConfigDict


class DifferenceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    a:float
    b:float
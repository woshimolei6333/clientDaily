from pydantic import BaseModel, field_validator, model_validator


class RegisterFrom(BaseModel):
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码长度不能小于 8 位")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    id: int
    username: str
    email: EmailStr ##自动做正则邮箱匹配

    # 使用Field增加元数据和约束条件
    age: int = Field(ge=0, le=120, description="年龄必须在1~120之间")
    # 这行代码表示定义了一个可选的个人简介（bio）字段，默认值为 None
    bio: Optional[str] = None

    #默认值工厂函数
    #记录生成时间戳,动态生成工厂（每次创建时执行函数）
    #每次 User() 生成实例时，才真正触发一次时间获取，保证时间的实时性。
    crated_at: datetime = Field(default_factory=datetime.utcnow)
if __name__ == '__main__':
    user = UserProfile(
        id="101",  # 字符串自动转为 int: 101
        username="coder",
        email="coder@example.com",
        age="25"  # 字符串自动转为 int: 25
    )
    print(user.id)  # 101 (int)
    print(type(user.age))  # <class 'int'>
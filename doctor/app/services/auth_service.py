from typing import Protocol, runtime_checkable
from pydantic import BaseModel

class User(BaseModel):
    """
    用户信息结构体
    """
    token: str
    user_id: str
    user_role: str

@runtime_checkable
class IAuthService(Protocol):
    """
    认证/鉴权服务
    """
    async def validate(self, token: str) -> bool:
        """
        验证 token 的有效性
        """
        ...
    
    async def get_user(self, token: str) -> User:
        """
        从 token 中提取用户信息
        """
        ...

class StubAuthService(IAuthService):
    """
    Stub 认证鉴权服务，总是通过所有的验证请求
    """
    async def validate(self, token: str) -> bool:
        return True
    
    async def get_user(self, token: str) -> User:
        """
        简单的 Stub 用户信息返回
        """
        return User(
            token=token,
            user_id="doctor_114514",
            user_role="doctor"
        )

def get_auth_service() -> IAuthService:
    return StubAuthService()

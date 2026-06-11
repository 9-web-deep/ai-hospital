from typing import Protocol, runtime_checkable

from fastapi import Header, Depends, HTTPException
from pydantic import BaseModel
from starlette import status


class User(BaseModel):
    token: str
    user_id: str
    user_role: str


@runtime_checkable
class IAuthService(Protocol):
    async def validate(self, token: str) -> bool: ...

    async def get_user(self, token: str) -> User: ...


class StubAuthService(IAuthService):
    async def validate(self, token: str) -> bool:
        return True

    async def get_user(self, token: str) -> User:
        return User(token=token, user_id="nurse_114514", user_role="nurse")


def get_auth_service() -> IAuthService:
    return StubAuthService()


async def verify_auth(
    authorization: str = Header(..., description="HTTP Auth Header"),
    auth_service: IAuthService = Depends(get_auth_service),
) -> User:
    if not await auth_service.validate(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return await auth_service.get_user(authorization)


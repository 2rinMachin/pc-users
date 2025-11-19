from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    client = "client"
    cook = "cook"
    dispatcher = "dispatcher"
    driver = "driver"
    admin = "admin"


class User(BaseModel):
    tenant_id: str
    user_id: str
    email: str
    username: str
    password: str
    role: UserRole


class UserResponseDto(BaseModel):
    tenant_id: str
    user_id: str
    email: str
    username: str
    role: UserRole


class SessionToken(BaseModel):
    token: str
    tenant_id: str
    user_id: str
    expires_at: str

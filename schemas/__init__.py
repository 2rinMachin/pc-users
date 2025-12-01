from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserRole(str, Enum):
    client = "client"
    cook = "cook"
    dispatcher = "dispatcher"
    driver = "driver"
    admin = "admin"


class Product(BaseModel):
    tenant_id: str
    product_id: str
    name: str
    price: Decimal
    image_url: Optional[str] = None


class OrderItem(BaseModel):
    product: Product
    quantity: int


class User(BaseModel):
    tenant_id: str
    user_id: str
    email: str
    username: str
    password: str
    role: UserRole


class AuthorizedUser(BaseModel):
    tenant_id: str
    user_id: str
    email: str
    username: str
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

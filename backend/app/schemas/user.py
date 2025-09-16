"""
User Schemas：用户视图与内部形态
"""
from typing import Optional
from .base import SchemaBase


class UserView(SchemaBase):
    user_id: int
    username: str
    email: str
    role: str
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    status: str


class GuestUserView(SchemaBase):
    username: str = 'guest'
    role: str = 'guest'

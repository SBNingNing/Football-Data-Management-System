"""
Auth Schemas：登录/注册/令牌响应与输入
"""
from typing import Optional
from pydantic import Field, EmailStr
from .base import SchemaBase
from .user import UserView, GuestUserView


# 输入
class RegisterIn(SchemaBase):
    username: str
    password: str
    email: EmailStr


class LoginIn(SchemaBase):
    username: str
    password: str


# 输出
class RegisterOut(SchemaBase):
    message: str = '注册成功'
    user_id: int


class LoginOut(SchemaBase):
    message: str = '登录成功'
    access_token: str
    user: UserView


class GuestLoginOut(SchemaBase):
    message: str = '游客登录成功'
    access_token: str
    user: GuestUserView = Field(default_factory=GuestUserView)

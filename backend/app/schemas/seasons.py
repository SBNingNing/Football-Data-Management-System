"""
Season 模块的 Pydantic Schemas
"""
from typing import Optional
from pydantic import Field
from .base import SchemaBase


class SeasonCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=50)
    # 与中间件/服务保持 ISO 字符串输入，由服务解析为 datetime
    start_time: str = Field(..., description='ISO-8601 格式')
    end_time: str = Field(..., description='ISO-8601 格式')


class SeasonUpdate(SchemaBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    start_time: Optional[str] = Field(None, description='ISO-8601 格式')
    end_time: Optional[str] = Field(None, description='ISO-8601 格式')


class SeasonOut(SchemaBase):
    season_id: int
    name: str
    start_time: Optional[str]
    end_time: Optional[str]

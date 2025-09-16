"""
Competitions 模块 Schemas：列表、详情、创建/更新输入。
"""
from typing import List, Optional, Dict, Any
from .base import SchemaBase


class CompetitionOut(SchemaBase):
    competition_id: int
    name: str


class CompetitionList(SchemaBase):
    competitions: List[CompetitionOut]
    statistics: Dict[str, Any]


class CompetitionCreate(SchemaBase):
    name: str


class CompetitionUpdate(SchemaBase):
    name: Optional[str] = None

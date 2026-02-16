"""
Events 模块 Schemas：create/update 输入与标准输出形态。
"""
from typing import Optional
from pydantic import Field, field_validator
from .base import SchemaBase


class EventCreate(SchemaBase):
    event_type: str
    match_id: Optional[str] = None
    team_id: Optional[int] = None
    player_id: Optional[str] = None
    event_time: Optional[int] = None
    match_name: Optional[str] = None
    player_name: Optional[str] = None

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        if v not in ('Goal', 'Card', 'Substitution'):
            raise ValueError("Event type must be 'Goal', 'Card', or 'Substitution'")
        return v


class EventUpdate(SchemaBase):
    event_type: Optional[str] = None
    event_time: Optional[int] = None
    player_name: Optional[str] = None


class EventOut(SchemaBase):
    id: int
    event_type: str
    match_id: str
    team_id: int
    player_id: str
    event_time: Optional[int] = None
    player_name: Optional[str] = None
    team_name: Optional[str] = None

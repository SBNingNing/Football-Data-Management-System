"""
Events 模块 Schemas：create/update 输入与标准输出形态。
"""
from typing import Optional
from pydantic import Field
from .base import SchemaBase


class EventCreate(SchemaBase):
    eventType: str
    matchId: Optional[str] = None
    teamId: Optional[int] = None
    playerId: Optional[str] = None
    eventTime: Optional[int] = None
    matchName: Optional[str] = None
    playerName: Optional[str] = None


class EventUpdate(SchemaBase):
    eventType: Optional[str] = None
    eventTime: Optional[int] = None
    playerName: Optional[str] = None


class EventOut(SchemaBase):
    id: int
    eventType: str
    matchId: str
    teamId: int
    playerId: str
    eventTime: Optional[int] = None
    playerName: Optional[str] = None
    teamName: Optional[str] = None

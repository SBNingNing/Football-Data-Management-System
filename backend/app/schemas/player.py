"""
球员相关的 Pydantic Schema
"""
from typing import Optional
from pydantic import Field
from .base import SchemaBase


class PlayerCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=50)
    student_id: str = Field(..., min_length=1, max_length=20, alias='studentId')


class PlayerUpdate(SchemaBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class PlayerOut(SchemaBase):
    id: str
    name: str
    career_goals: int
    career_red_cards: int
    career_yellow_cards: int

"""
Matches 模块 Schemas：create/update/detail 与 records 分页。
"""
from typing import List, Optional
from pydantic import field_validator
from .base import SchemaBase, Page, PageMeta


class MatchCreate(SchemaBase):
    match_name: str
    match_time: str
    location: str
    home_team_id: int
    away_team_id: int
    tournament_id: Optional[int] = None
    competition_id: Optional[int] = None
    match_type: Optional[str] = None
    group_id: Optional[str] = None


class MatchUpdate(SchemaBase):
    match_name: Optional[str] = None
    match_time: Optional[str] = None
    location: Optional[str] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    group_id: Optional[str] = None
    status: Optional[str] = None
    knockout_round: Optional[int] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('F', 'P'):
            raise ValueError("Status must be 'F' (Finished) or 'P' (Pending)")
        return v


class MatchBrief(SchemaBase):
    id: str
    match_name: str
    match_time: Optional[str]
    location: str
    home_team_id: Optional[int]
    home_team_name: Optional[str]
    away_team_id: Optional[int]
    away_team_name: Optional[str]
    home_score: int
    away_score: int
    group_id: Optional[str]
    tournament_id: int
    tournament_name: Optional[str]
    status: str
    knockout_round: Optional[int]


class MatchRecordItem(SchemaBase):
    id: int
    match_name: str
    match_time: str
    location: str
    home_team: str
    away_team: str
    score: str
    status: str
    match_type: Optional[str]


class MatchRecordsPage(Page[MatchRecordItem]):
    meta: PageMeta

"""
Matches 模块 Schemas：create/update/detail 与 records 分页。
"""
from typing import List, Optional
from .base import SchemaBase, Page, PageMeta


class MatchCreate(SchemaBase):
    matchName: str
    matchTime: str
    location: str
    homeTeamId: int
    awayTeamId: int
    tournamentId: int
    groupId: Optional[str] = None


class MatchUpdate(SchemaBase):
    matchName: Optional[str] = None
    matchTime: Optional[str] = None
    location: Optional[str] = None
    homeTeamId: Optional[int] = None
    awayTeamId: Optional[int] = None
    groupId: Optional[str] = None
    status: Optional[str] = None
    knockoutRound: Optional[int] = None


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
    id: str
    matchName: str
    matchTime: str
    location: str
    homeTeam: str
    awayTeam: str
    score: str
    status: str
    matchType: Optional[str]


class MatchRecordsPage(Page[MatchRecordItem]):
    meta: PageMeta

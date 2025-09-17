"""
Tournaments 模块 Schemas：覆盖列表/详情常见输出与创建/更新输入。
"""
from typing import List, Optional
from .base import SchemaBase


class TournamentRecord(SchemaBase):
    id: int
    name: str
    tournamentName: str
    teams: List[dict]
    teamCount: int
    totalGoals: int
    totalTeams: int
    matches: List[dict]
    matchCount: int
    seasonStartTime: Optional[str]
    seasonEndTime: Optional[str]
    isGrouped: bool
    seasonName: str


class TournamentInfo(SchemaBase):
    tournamentName: str
    totalSeasons: int
    records: List[TournamentRecord]
    matchedMode: Optional[str] = None


class TournamentCreate(SchemaBase):
    name: str
    season_name: str
    is_grouped: Optional[bool] = False
    season_start_time: Optional[str] = None
    season_end_time: Optional[str] = None


class TournamentUpdate(SchemaBase):
    name: Optional[str] = None
    season_name: Optional[str] = None
    is_grouped: Optional[bool] = None
    season_start_time: Optional[str] = None
    season_end_time: Optional[str] = None


class TournamentInstanceCreate(SchemaBase):
    competition_id: int
    season_id: int
    is_grouped: Optional[bool] = False
    group_count: Optional[int] = None
    playoff_spots: Optional[int] = None


class TournamentInstanceUpdate(SchemaBase):
    competition_id: Optional[int] = None
    season_id: Optional[int] = None
    is_grouped: Optional[bool] = None
    group_count: Optional[int] = None
    playoff_spots: Optional[int] = None

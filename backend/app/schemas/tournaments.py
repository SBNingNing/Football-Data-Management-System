"""
Tournaments 模块 Schemas：覆盖列表/详情常见输出与创建/更新输入。
"""
from typing import List, Optional
from .base import SchemaBase


class TournamentRecord(SchemaBase):
    id: int
    name: str
    tournament_name: str
    teams: List[dict]
    team_count: int
    total_goals: int
    total_teams: int
    matches: List[dict]
    match_count: int
    season_start_time: Optional[str]
    season_end_time: Optional[str]
    is_grouped: bool
    season_name: str


class TournamentInfo(SchemaBase):
    tournament_name: str
    total_seasons: int
    records: List[TournamentRecord]
    matched_mode: Optional[str] = None


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
    group_count: Optional[int] = None
    playoff_spots: Optional[int] = None


class TournamentInstanceCreate(SchemaBase):
    competition_id: int
    season_id: int
    is_grouped: Optional[bool] = False
    group_count: Optional[int] = None
    playoff_spots: Optional[int] = None


class TournamentQuickCreate(SchemaBase):
    competition_id: Optional[int] = None
    competition_name: Optional[str] = None
    season_id: Optional[int] = None
    season_name: Optional[str] = None
    create_if_missing: Optional[bool] = True
    dry_run: Optional[bool] = False
    is_grouped: Optional[bool] = False
    group_count: Optional[int] = None
    playoff_spots: Optional[int] = None


class TournamentInstanceUpdate(SchemaBase):
    competition_id: Optional[int] = None
    season_id: Optional[int] = None
    is_grouped: Optional[bool] = None
    group_count: Optional[int] = None
    playoff_spots: Optional[int] = None

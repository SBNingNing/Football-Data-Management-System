"""
Teams 模块 Schemas：覆盖 Team 视图与 Participation 视图的常用输出形态。
注意：Team 是只读 VIEW；写入通过 Participation 完成。
"""
from typing import List, Optional
from pydantic import Field, field_validator
from .base import SchemaBase


class TeamView(SchemaBase):
    id: int
    team_name: str
    tournament_id: Optional[int] = None
    tournament_name: Optional[str] = None
    group_id: Optional[str] = None
    rank: Optional[int]
    goals: int
    goals_conceded: int
    goal_difference: int
    red_cards: int
    yellow_cards: int
    points: int


class PlayerBrief(SchemaBase):
    name: Optional[str]
    id: Optional[str] = None
    student_id: str
    number: str
    goals: int = 0
    red_cards: int = 0
    yellow_cards: int = 0


class ParticipationView(TeamView):
    players: List[PlayerBrief] = Field(default_factory=list)
    matches_played: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None


class TeamCreate(SchemaBase):
    team_name: str
    tournament_id: Optional[int] = None
    competition_id: Optional[int] = None
    competition_name: Optional[str] = None
    season_name: Optional[str] = None
    group_id: Optional[str] = None
    players: List[PlayerBrief] = Field(default_factory=list)


class TeamUpdate(SchemaBase):
    team_name: Optional[str] = None
    match_type: Optional[str] = None
    group_id: Optional[str] = None
    players: Optional[List[PlayerBrief]] = None

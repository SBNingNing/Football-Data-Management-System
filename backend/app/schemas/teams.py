"""
Teams 模块 Schemas：覆盖 Team 视图与 Participation 视图的常用输出形态。
注意：Team 是只读 VIEW；写入通过 Participation 完成。
"""
from typing import List, Optional
from pydantic import Field
from .base import SchemaBase


class TeamView(SchemaBase):
    id: int
    name: str = Field(..., alias='teamName')
    tournament_id: Optional[int] = Field(None, alias='tournamentId')
    tournament_name: Optional[str] = Field(None, alias='tournamentName')
    group_id: Optional[str] = Field(None, alias='groupId')
    rank: Optional[int]
    goals: int
    goalsConceded: int
    goalDifference: int
    redCards: int
    yellowCards: int
    points: int


class PlayerBrief(SchemaBase):
    name: Optional[str]
    id: str
    studentId: str
    number: str
    goals: int
    redCards: int
    yellowCards: int


class ParticipationView(TeamView):
    players: List[PlayerBrief] = Field(default_factory=list)
    matchesPlayed: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None


class TeamCreate(SchemaBase):
    teamName: str
    tournamentId: Optional[int] = None
    competitionName: Optional[str] = None
    seasonName: Optional[str] = None
    groupId: Optional[str] = None
    players: List[PlayerBrief] = Field(default_factory=list)


class TeamUpdate(SchemaBase):
    teamName: Optional[str] = None
    matchType: Optional[str] = None
    groupId: Optional[str] = None
    players: Optional[List[PlayerBrief]] = None

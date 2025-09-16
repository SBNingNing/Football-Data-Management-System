"""
Stats 模块 Schemas（Pydantic v2）：overview、rankings、tournament 统计。
与服务层返回结构保持一致，主要用于类型约束与可选的出参序列化。
"""
from typing import Dict, List, Optional
from pydantic import RootModel
from .base import SchemaBase


class StatsOverview(SchemaBase):
    totalMatches: int
    completedMatches: int
    upcomingMatches: int


# ---- Rankings ----
class TopScorerPlayer(SchemaBase):
    id: str
    name: str
    team: Optional[str]
    goals: int


class TopScorerTeam(SchemaBase):
    team: str
    goals: int


class CardPlayer(SchemaBase):
    id: str
    name: str
    team: Optional[str]
    yellowCards: int
    redCards: int


class CardTeam(SchemaBase):
    team: str
    yellowCards: int
    redCards: int


class PointsRankingItem(SchemaBase):
    team: str
    matchesPlayed: int
    points: int
    goalsFor: int
    goalsAgainst: int
    goalDifference: int
    rank: int


class RankingsBlock(SchemaBase):
    # {'players': List[TopScorerPlayer], 'teams': List[TopScorerTeam]}
    topScorers: Dict[str, List]
    # {'players': List[CardPlayer], 'teams': List[CardTeam]}
    cards: Dict[str, List]
    points: List[PointsRankingItem]


class Rankings(RootModel[Dict[str, RankingsBlock]]):
    pass


# ---- Tournament stats ----
class TournamentRef(SchemaBase):
    id: int
    name: str


class MatchesStats(SchemaBase):
    total: int
    completed: int
    remaining: int


class TeamsStats(SchemaBase):
    total: int


class GoalsStats(SchemaBase):
    total: int
    average_per_match: float


class TournamentStats(SchemaBase):
    tournament: TournamentRef
    matches: MatchesStats
    teams: TeamsStats
    goals: GoalsStats

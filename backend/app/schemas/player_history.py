"""
Player History 模块 Schemas：请求与响应模型，贴合现有服务返回结构。
"""
from typing import List, Optional, Dict, Any
from .base import SchemaBase


# 基础信息
class PlayerInfo(SchemaBase):
    id: str
    name: str
    career_goals: int = 0
    career_red_cards: int = 0
    career_yellow_cards: int = 0


class TournamentInfo(SchemaBase):
    id: int
    name: str
    season_name: Optional[str] = None


class TeamChangeRecord(SchemaBase):
    team_name: str
    tournament_info: TournamentInfo | Dict[str, Any]
    goals_scored: int = 0
    yellow_cards: int = 0
    red_cards: int = 0


# complete 接口（跨赛季历史）
class SeasonSummary(SchemaBase):
    season_name: str
    tournaments_participated: int
    teams_played_for: int
    total_goals: int
    total_yellow_cards: int
    total_red_cards: int


class SeasonBlock(SchemaBase):
    season_name: str
    teams: List[TeamChangeRecord]
    season_summary: SeasonSummary


class PlayerCompleteHistoryOut(SchemaBase):
    player_info: PlayerInfo
    seasons: List[SeasonBlock]
    career_summary: Dict[str, Any]  # 来自 calculate_career_statistics，字段结构固定但这里保持兼容映射


# 赛季表现接口
class SeasonInfo(SchemaBase):
    id: int
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class SeasonTotals(SchemaBase):
    total_goals: int = 0
    total_yellow_cards: int = 0
    total_red_cards: int = 0
    tournaments_participated: int = 0
    teams_played_for: int = 0


class PlayerSeasonPerformanceOut(SchemaBase):
    player_info: PlayerInfo
    season_info: SeasonInfo
    performance: List[TeamChangeRecord]
    season_totals: SeasonTotals


# 对比接口
class PlayerComparisonIn(SchemaBase):
    player_ids: List[str]
    season_ids: Optional[List[int]] = None


class DisciplinaryRecord(SchemaBase):
    yellow_card_rate: float = 0
    red_card_rate: float = 0


class PlayerComparisonItem(SchemaBase):
    player_info: PlayerInfo
    total_goals: int
    total_yellow_cards: int
    total_red_cards: int
    seasons_played: int
    tournaments_participated: int
    teams_played_for: int
    average_goals_per_tournament: float
    disciplinary_record: DisciplinaryRecord


class PlayerComparisonOut(SchemaBase):
    comparison: List[PlayerComparisonItem]
    comparison_metadata: Dict[str, Any]


# 转队历史
class PlayerTeamChangesOut(SchemaBase):
    player_info: PlayerInfo
    team_changes: List[TeamChangeRecord]
    summary: Dict[str, Any]  # {total_teams, total_transfers}

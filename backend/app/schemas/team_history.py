"""
Team History 模块 Schemas：请求与响应模型，贴合现有服务返回结构。
"""
from typing import List, Optional, Dict, Any, Union
from .base import SchemaBase


# 基础信息
class TeamInfo(SchemaBase):
    id: Union[str, int]
    name: str
    city: Optional[str] = None
    founded_year: Optional[int] = None


class SeasonInfo(SchemaBase):
    id: int
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# 赛事条目与统计
class TournamentStats(SchemaBase):
    players_count: int = 0
    total_goals: int = 0
    total_yellow_cards: int = 0
    total_red_cards: int = 0


class TournamentRecord(SchemaBase):
    tournament_id: int
    tournament_name: str
    competition_name: Optional[str] = None
    team_id: Union[str, int]
    team_name: Optional[str] = None
    final_ranking: Optional[int] = None
    remarks: Optional[str] = None
    stats: TournamentStats


# 赛季聚合（complete 接口使用）
class SeasonTotalsComplete(SchemaBase):
    tournaments_count: int = 0
    total_players: int = 0
    total_goals: int = 0
    total_yellow_cards: int = 0
    total_red_cards: int = 0


class SeasonBlock(SchemaBase):
    season_info: SeasonInfo
    tournaments: List[TournamentRecord]
    season_totals: SeasonTotalsComplete


# 职业生涯汇总
class DisciplinaryRecord(SchemaBase):
    yellow_card_rate: float = 0
    red_card_rate: float = 0


class CareerSummary(SchemaBase):
    total_tournaments: int = 0
    total_seasons: int = 0
    total_players_used: int = 0
    total_goals_scored: int = 0
    total_yellow_cards: int = 0
    total_red_cards: int = 0
    best_ranking: Optional[int] = None
    average_ranking: Optional[float] = None
    average_goals_per_tournament: float = 0
    disciplinary_record: DisciplinaryRecord


# GET /team_history/<team_base_id>/complete 响应
class TeamCompleteHistoryOut(SchemaBase):
    team_info: TeamInfo
    seasons: List[SeasonBlock]
    career_summary: CareerSummary


# GET /team_history/<team_base_id>/season/<season_id> 响应（season_totals 字段结构与 complete 不同，保留原状）
class TeamSeasonPerformanceOut(SchemaBase):
    team_info: TeamInfo
    season_info: SeasonInfo
    performance: List[TournamentRecord]
    # 原服务返回的 season_totals: {tournaments_participated,total_players,total_goals,total_yellow_cards,total_red_cards,average_ranking}
    # 为避免破坏现有结构，保持为任意映射
    season_totals: Dict[str, Any]


# POST /team_history/compare 请求与响应
class TeamComparisonIn(SchemaBase):
    team_base_ids: List[Union[str, int]]
    season_ids: Optional[List[int]] = None


class TeamComparisonItem(SchemaBase):
    team_info: TeamInfo
    total_tournaments: int
    total_seasons: int
    total_players_used: int
    total_goals_scored: int
    total_yellow_cards: int
    total_red_cards: int
    best_ranking: Optional[int] = None
    average_ranking: Optional[float] = None
    average_goals_per_tournament: float = 0
    disciplinary_record: DisciplinaryRecord


class TeamComparisonOut(SchemaBase):
    comparison: List[TeamComparisonItem]
    comparison_metadata: Dict[str, Any]


# GET /team_history/tournament-history/<team_base_id> 响应
class TournamentHistoryRecord(SchemaBase):
    season_name: Optional[str] = None
    tournament_name: Optional[str] = None
    competition_name: Optional[str] = None
    team_name: Optional[str] = None
    final_ranking: Optional[int] = None
    remarks: Optional[str] = None


class TeamTournamentHistoryOut(SchemaBase):
    team_info: TeamInfo
    tournament_history: List[TournamentHistoryRecord]
    # 原服务返回 summary: {total_tournaments,total_seasons,best_ranking}
    summary: Dict[str, Any]

"""
球员历史查询模块工具类
提供球员历史数据处理的专用工具函数
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from collections import defaultdict
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PlayerHistoryUtils:
    """球员历史查询工具类"""

    @staticmethod
    def validate_player_id(player_id: str) -> bool:
        """验证球员ID格式"""
        return bool(player_id and player_id.strip())

    @staticmethod
    def validate_season_id(season_id: Any) -> bool:
        """验证赛季ID格式"""
        try:
            return isinstance(season_id, int) and season_id > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def safe_date_format(date_obj) -> Optional[str]:
        """安全的日期格式化"""
        try:
            return date_obj.isoformat() if date_obj else None
        except (AttributeError, ValueError):
            return None

    @staticmethod
    def calculate_average_safely(total: float, count: int, decimal_places: int = 2) -> float:
        """安全的平均值计算"""
        try:
            return round(total / count, decimal_places) if count > 0 else 0
        except (ValueError, TypeError, ZeroDivisionError):
            return 0

    @staticmethod
    def format_player_basic_info(player) -> Dict[str, Any]:
        """格式化球员基础信息"""
        if not player:
            return {}
        
        return {
            'id': player.id,
            'name': player.name or '未知球员',
            'career_goals': getattr(player, 'career_goals', 0) or 0,
            'career_red_cards': getattr(player, 'career_red_cards', 0) or 0,
            'career_yellow_cards': getattr(player, 'career_yellow_cards', 0) or 0
        }

    @staticmethod
    def group_histories_by_season(histories: List) -> Dict[str, List]:
        """按赛季分组历史记录"""
        grouped = defaultdict(list)
        try:
            for history in histories:
                if (hasattr(history, 'tournament') and 
                    history.tournament and 
                    hasattr(history.tournament, 'season') and
                    history.tournament.season and
                    hasattr(history.tournament.season, 'name')):
                    season_name = history.tournament.season.name
                    grouped[season_name].append(history)
        except (AttributeError, TypeError) as e:
            logger.warning(f"按赛季分组球员历史记录时出错: {e}")
        
        return dict(grouped)

    @staticmethod
    def calculate_career_statistics(histories: List) -> Dict[str, Any]:
        """计算球员职业生涯统计"""
        if not histories:
            return PlayerHistoryUtils.get_empty_career_summary()
        
        total_goals = sum(getattr(h, 'tournament_goals', 0) or 0 for h in histories)
        total_yellow_cards = sum(getattr(h, 'tournament_yellow_cards', 0) or 0 for h in histories)
        total_red_cards = sum(getattr(h, 'tournament_red_cards', 0) or 0 for h in histories)
        
        seasons = PlayerHistoryUtils.extract_unique_seasons(histories)
        tournaments = PlayerHistoryUtils.extract_unique_tournaments(histories)
        teams = PlayerHistoryUtils.extract_unique_teams(histories)
        
        return {
            'total_goals': total_goals,
            'total_yellow_cards': total_yellow_cards,
            'total_red_cards': total_red_cards,
            'seasons_played': len(seasons),
            'tournaments_participated': len(tournaments),
            'teams_played_for': len(teams),
            'average_goals_per_tournament': PlayerHistoryUtils.calculate_average_safely(
                total_goals, len(tournaments)
            ),
            'disciplinary_record': {
                'yellow_card_rate': PlayerHistoryUtils.calculate_average_safely(
                    total_yellow_cards, len(tournaments)
                ),
                'red_card_rate': PlayerHistoryUtils.calculate_average_safely(
                    total_red_cards, len(tournaments)
                )
            }
        }

    @staticmethod
    def build_team_change_record(history) -> Dict[str, Any]:
        """构建转队记录"""
        try:
            team_name = None
            if hasattr(history, 'team') and history.team:
                if (hasattr(history.team, 'team_base') and 
                    history.team.team_base and 
                    hasattr(history.team.team_base, 'name')):
                    team_name = history.team.team_base.name
                elif hasattr(history.team, 'name'):
                    team_name = history.team.name
            
            tournament_info = {}
            if hasattr(history, 'tournament') and history.tournament:
                tournament_info = {
                    'id': history.tournament.id,
                    'name': history.tournament.name,
                    'season_name': (
                        history.tournament.season.name 
                        if history.tournament.season else None
                    )
                }
            
            return {
                'team_name': team_name or '未知球队',
                'tournament_info': tournament_info,
                'goals_scored': getattr(history, 'tournament_goals', 0) or 0,
                'yellow_cards': getattr(history, 'tournament_yellow_cards', 0) or 0,
                'red_cards': getattr(history, 'tournament_red_cards', 0) or 0
            }
        except AttributeError:
            return {
                'team_name': '未知球队',
                'tournament_info': {},
                'goals_scored': 0,
                'yellow_cards': 0,
                'red_cards': 0
            }

    @staticmethod
    def format_season_summary(season_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化赛季汇总数据"""
        histories = season_data.get('histories', [])
        
        return {
            'season_name': season_data.get('season_name', '未知赛季'),
            'tournaments_participated': len(set(
                h.tournament.name for h in histories 
                if h.tournament and h.tournament.name
            )),
            'teams_played_for': len(set(
                PlayerHistoryUtils._get_team_name(h) for h in histories
            )),
            'total_goals': sum(getattr(h, 'tournament_goals', 0) or 0 for h in histories),
            'total_yellow_cards': sum(getattr(h, 'tournament_yellow_cards', 0) or 0 for h in histories),
            'total_red_cards': sum(getattr(h, 'tournament_red_cards', 0) or 0 for h in histories)
        }

    @staticmethod
    def extract_unique_tournaments(histories: List) -> Set[str]:
        """提取唯一赛事"""
        tournaments = set()
        for history in histories:
            try:
                if (hasattr(history, 'tournament') and 
                    history.tournament and 
                    hasattr(history.tournament, 'name')):
                    tournaments.add(history.tournament.name)
            except AttributeError:
                continue
        return tournaments

    @staticmethod
    def extract_unique_seasons(histories: List) -> Set[str]:
        """提取唯一赛季"""
        seasons = set()
        for history in histories:
            try:
                if (hasattr(history, 'tournament') and 
                    history.tournament and 
                    hasattr(history.tournament, 'season') and
                    history.tournament.season and
                    hasattr(history.tournament.season, 'name')):
                    seasons.add(history.tournament.season.name)
            except AttributeError:
                continue
        return seasons

    @staticmethod
    def extract_unique_teams(histories: List) -> Set[str]:
        """提取唯一球队"""
        teams = set()
        for history in histories:
            try:
                team_name = PlayerHistoryUtils._get_team_name(history)
                if team_name:
                    teams.add(team_name)
            except AttributeError:
                continue
        return teams

    @staticmethod
    def _get_team_name(history) -> Optional[str]:
        """从历史记录获取球队名称"""
        try:
            if hasattr(history, 'team') and history.team:
                if (hasattr(history.team, 'team_base') and 
                    history.team.team_base and 
                    hasattr(history.team.team_base, 'name')):
                    return history.team.team_base.name
                elif hasattr(history.team, 'name'):
                    return history.team.name
            return None
        except AttributeError:
            return None

    @staticmethod
    def get_empty_career_summary() -> Dict[str, Any]:
        """获取空的职业生涯汇总"""
        return {
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'seasons_played': 0,
            'tournaments_participated': 0,
            'teams_played_for': 0,
            'average_goals_per_tournament': 0,
            'disciplinary_record': {
                'yellow_card_rate': 0,
                'red_card_rate': 0
            }
        }

    @staticmethod
    def get_empty_season_totals() -> Dict[str, Any]:
        """获取空的赛季统计"""
        return {
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'tournaments_participated': 0,
            'teams_played_for': 0
        }

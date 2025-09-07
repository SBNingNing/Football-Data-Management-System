"""
球队历史查询模块工具类
提供球队历史数据处理的专用工具函数
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from collections import defaultdict
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TeamHistoryUtils:
    """球队历史查询工具类"""

    @staticmethod
    def validate_team_base_id(team_base_id: Any) -> bool:
        """验证球队基础ID格式"""
        try:
            if team_base_id is None:
                return False
            team_id_str = str(team_base_id).strip()
            return bool(team_id_str)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_season_id(season_id: Any) -> bool:
        """验证赛季ID格式"""
        try:
            return isinstance(season_id, int) and season_id > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_team_ids_list(team_base_ids: List[Any], min_count: int = 1, max_count: int = 10) -> bool:
        """验证球队ID列表"""
        return (
            isinstance(team_base_ids, list) and 
            min_count <= len(team_base_ids) <= max_count and 
            all(TeamHistoryUtils.validate_team_base_id(tid) for tid in team_base_ids if tid is not None)
        )

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
    def format_team_basic_info(team_base) -> Dict[str, Any]:
        """格式化球队基础信息"""
        if not team_base:
            return {}
        
        return {
            'id': team_base.id,
            'name': team_base.name or '未知球队',
            'city': getattr(team_base, 'city', None),
            'founded_year': getattr(team_base, 'founded_year', None)
        }

    @staticmethod
    def group_participations_by_season(participations: List) -> Dict[str, List]:
        """按赛季分组参赛记录"""
        grouped = defaultdict(list)
        try:
            for participation in participations:
                if (hasattr(participation, 'tournament') and 
                    participation.tournament and 
                    hasattr(participation.tournament, 'season') and
                    participation.tournament.season and
                    hasattr(participation.tournament.season, 'name')):
                    season_name = participation.tournament.season.name
                    grouped[season_name].append(participation)
        except (AttributeError, TypeError) as e:
            logger.warning(f"按赛季分组球队参赛记录时出错: {e}")
        
        return dict(grouped)

    @staticmethod
    def calculate_tournament_player_stats(team_id: str, tournament_id: int) -> Dict[str, Any]:
        """计算赛事中的球员统计"""
        try:
            from app.models import PlayerTeamHistory
            
            players_stats = PlayerTeamHistory.query.filter_by(
                team_id=team_id,
                tournament_id=tournament_id
            ).all()
            
            return {
                'players_count': len(players_stats),
                'total_goals': sum(p.tournament_goals for p in players_stats if p.tournament_goals),
                'total_yellow_cards': sum(p.tournament_yellow_cards for p in players_stats if p.tournament_yellow_cards),
                'total_red_cards': sum(p.tournament_red_cards for p in players_stats if p.tournament_red_cards)
            }
        except Exception as e:
            logger.warning(f"计算赛事球员统计时出错: {e}")
            return {
                'players_count': 0,
                'total_goals': 0,
                'total_yellow_cards': 0,
                'total_red_cards': 0
            }

    @staticmethod
    def calculate_season_totals(participations: List) -> Dict[str, Any]:
        """计算赛季统计汇总"""
        if not participations:
            return TeamHistoryUtils.get_empty_season_totals()
        
        season_totals = {
            'tournaments_participated': len(participations),
            'total_players': 0,
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'average_ranking': 0
        }
        
        total_ranking = 0
        ranking_count = 0
        
        for participation in participations:
            try:
                tournament_stats = TeamHistoryUtils.calculate_tournament_player_stats(
                    participation.team_id,
                    participation.tournament_id if hasattr(participation, 'tournament_id') else None
                )
                
                season_totals['total_players'] += tournament_stats['players_count']
                season_totals['total_goals'] += tournament_stats['total_goals']
                season_totals['total_yellow_cards'] += tournament_stats['total_yellow_cards']
                season_totals['total_red_cards'] += tournament_stats['total_red_cards']
                
                if hasattr(participation, 'final_ranking') and participation.final_ranking:
                    total_ranking += participation.final_ranking
                    ranking_count += 1
                    
            except AttributeError:
                continue
        
        if ranking_count > 0:
            season_totals['average_ranking'] = TeamHistoryUtils.calculate_average_safely(
                total_ranking, ranking_count
            )
        
        return season_totals

    @staticmethod
    def calculate_career_summary(participations: List) -> Dict[str, Any]:
        """计算球队职业生涯汇总统计"""
        if not participations:
            return TeamHistoryUtils.get_empty_career_summary()
        
        seasons = set()
        tournaments = set()
        rankings = []
        total_players = 0
        total_goals = 0
        total_yellow_cards = 0
        total_red_cards = 0
        
        for participation in participations:
            try:
                if participation.tournament and participation.tournament.season:
                    seasons.add(participation.tournament.season.name)
                    tournaments.add(participation.tournament.name)
                
                if hasattr(participation, 'final_ranking') and participation.final_ranking:
                    rankings.append(participation.final_ranking)
                
                tournament_stats = TeamHistoryUtils.calculate_tournament_player_stats(
                    participation.team_id,
                    participation.tournament_id if hasattr(participation, 'tournament_id') else None
                )
                
                total_players += tournament_stats['players_count']
                total_goals += tournament_stats['total_goals']
                total_yellow_cards += tournament_stats['total_yellow_cards']
                total_red_cards += tournament_stats['total_red_cards']
                
            except AttributeError:
                continue
        
        return {
            'total_tournaments': len(tournaments),
            'total_seasons': len(seasons),
            'total_players_used': total_players,
            'total_goals_scored': total_goals,
            'total_yellow_cards': total_yellow_cards,
            'total_red_cards': total_red_cards,
            'best_ranking': min(rankings) if rankings else None,
            'average_ranking': TeamHistoryUtils.calculate_average_safely(
                sum(rankings), len(rankings)
            ) if rankings else None,
            'average_goals_per_tournament': TeamHistoryUtils.calculate_average_safely(
                total_goals, len(tournaments)
            ) if tournaments else 0,
            'disciplinary_record': {
                'yellow_card_rate': TeamHistoryUtils.calculate_average_safely(
                    total_yellow_cards, len(tournaments)
                ) if tournaments else 0,
                'red_card_rate': TeamHistoryUtils.calculate_average_safely(
                    total_red_cards, len(tournaments)
                ) if tournaments else 0
            }
        }

    @staticmethod
    def validate_comparison_data(data: Dict[str, Any]) -> List[str]:
        """验证球队对比数据"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append('请求数据格式错误')
            return errors
        
        team_base_ids = data.get('team_base_ids', [])
        if not TeamHistoryUtils.validate_team_ids_list(team_base_ids, min_count=1, max_count=10):
            errors.append('请提供有效的球队ID列表（1-10个球队）')
        
        season_ids = data.get('season_ids', [])
        if season_ids and not all(TeamHistoryUtils.validate_season_id(sid) for sid in season_ids):
            errors.append('赛季ID格式错误')
        
        return errors

    @staticmethod
    def get_empty_career_summary() -> Dict[str, Any]:
        """获取空的职业生涯汇总"""
        return {
            'total_tournaments': 0,
            'total_seasons': 0,
            'total_players_used': 0,
            'total_goals_scored': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'best_ranking': None,
            'average_ranking': None,
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
            'tournaments_participated': 0,
            'total_players': 0,
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'average_ranking': 0
        }

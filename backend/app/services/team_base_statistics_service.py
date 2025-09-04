"""
TeamBase 统计服务
处理球队基础信息相关的统计计算和业务逻辑
"""

from typing import List, Dict, Optional, Any
from app.models.team_base import TeamBase


class TeamBaseStatisticsService:
    """球队基础统计服务"""
    
    @staticmethod
    def calculate_team_historical_stats(team_base: TeamBase) -> Dict[str, Any]:
        """计算球队历史统计数据"""
        if not team_base.participations:
            return TeamBaseStatisticsService._get_empty_stats()
        
        participations = team_base.participations
        
        # 基础统计
        total_tournaments = len(participations)
        total_goals = sum(p.tournament_goals for p in participations)
        total_goals_conceded = sum(p.goals_conceded for p in participations)
        total_points = sum(p.points for p in participations)
        total_matches = sum(p.matches_played for p in participations)
        total_wins = sum(p.wins for p in participations)
        total_draws = sum(p.draws for p in participations)
        total_losses = sum(p.losses for p in participations)
        total_red_cards = sum(p.red_cards for p in participations)
        total_yellow_cards = sum(p.yellow_cards for p in participations)
        
        # 计算衍生统计
        goal_difference = total_goals - total_goals_conceded
        win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0.0
        draw_rate = (total_draws / total_matches * 100) if total_matches > 0 else 0.0
        loss_rate = (total_losses / total_matches * 100) if total_matches > 0 else 0.0
        avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0.0
        avg_goals_conceded_per_match = total_goals_conceded / total_matches if total_matches > 0 else 0.0
        avg_points_per_match = total_points / total_matches if total_matches > 0 else 0.0
        
        # 最佳排名
        valid_ranks = [p.rank for p in participations if p.rank and p.rank > 0]
        best_rank = min(valid_ranks) if valid_ranks else None
        
        return {
            'basic_stats': {
                'total_tournaments': total_tournaments,
                'total_matches_played': total_matches,
                'total_wins': total_wins,
                'total_draws': total_draws,
                'total_losses': total_losses,
                'total_points': total_points
            },
            'goal_stats': {
                'total_goals': total_goals,
                'total_goals_conceded': total_goals_conceded,
                'goal_difference': goal_difference,
                'avg_goals_per_match': round(avg_goals_per_match, 2),
                'avg_goals_conceded_per_match': round(avg_goals_conceded_per_match, 2)
            },
            'performance_stats': {
                'win_rate': round(win_rate, 2),
                'draw_rate': round(draw_rate, 2),
                'loss_rate': round(loss_rate, 2),
                'avg_points_per_match': round(avg_points_per_match, 2),
                'best_rank': best_rank
            },
            'discipline_stats': {
                'total_red_cards': total_red_cards,
                'total_yellow_cards': total_yellow_cards,
                'avg_red_cards_per_match': round(total_red_cards / total_matches, 2) if total_matches > 0 else 0.0,
                'avg_yellow_cards_per_match': round(total_yellow_cards / total_matches, 2) if total_matches > 0 else 0.0
            }
        }
    
    @staticmethod
    def _get_empty_stats() -> Dict[str, Any]:
        """返回空的统计数据"""
        return {
            'basic_stats': {
                'total_tournaments': 0,
                'total_matches_played': 0,
                'total_wins': 0,
                'total_draws': 0,
                'total_losses': 0,
                'total_points': 0
            },
            'goal_stats': {
                'total_goals': 0,
                'total_goals_conceded': 0,
                'goal_difference': 0,
                'avg_goals_per_match': 0.0,
                'avg_goals_conceded_per_match': 0.0
            },
            'performance_stats': {
                'win_rate': 0.0,
                'draw_rate': 0.0,
                'loss_rate': 0.0,
                'avg_points_per_match': 0.0,
                'best_rank': None
            },
            'discipline_stats': {
                'total_red_cards': 0,
                'total_yellow_cards': 0,
                'avg_red_cards_per_match': 0.0,
                'avg_yellow_cards_per_match': 0.0
            }
        }
    
    @staticmethod
    def get_team_participation_by_tournament(team_base: TeamBase, tournament_id: int):
        """获取指定赛事的参赛记录"""
        for participation in team_base.participations:
            if participation.tournament_id == tournament_id:
                return participation
        return None
    
    @staticmethod
    def get_recent_participations(team_base: TeamBase, limit: int = 5) -> List:
        """获取最近的参赛记录"""
        if not team_base.participations:
            return []
        
        # 按赛事ID倒序排列（假设赛事ID越大越新）
        sorted_participations = sorted(
            team_base.participations, 
            key=lambda p: p.tournament_id, 
            reverse=True
        )
        return sorted_participations[:limit]
    
    @staticmethod
    def compare_team_performance(team_base_ids: List[int]) -> Dict[str, Any]:
        """比较多个球队的历史表现"""
        from app.models.team_base import TeamBase
        
        teams_data = []
        
        for team_id in team_base_ids:
            team = TeamBase.query.get(team_id)
            if team:
                stats = TeamBaseStatisticsService.calculate_team_historical_stats(team)
                teams_data.append({
                    'team_id': team.id,
                    'team_name': team.name,
                    'stats': stats
                })
        
        return {
            'comparison_date': datetime.utcnow().isoformat(),
            'teams_count': len(teams_data),
            'teams_data': teams_data
        }
    
    @staticmethod
    def get_top_teams_by_criteria(criteria: str = 'win_rate', limit: int = 10) -> List[Dict[str, Any]]:
        """根据指定标准获取排名前列的球队"""
        from app.models.team_base import TeamBase
        
        all_teams = TeamBase.query.all()
        teams_with_stats = []
        
        for team in all_teams:
            if team.participations:  # 只包含有参赛记录的球队
                stats = TeamBaseStatisticsService.calculate_team_historical_stats(team)
                teams_with_stats.append({
                    'team_id': team.id,
                    'team_name': team.name,
                    'stats': stats
                })
        
        # 根据不同标准排序
        if criteria == 'win_rate':
            teams_with_stats.sort(
                key=lambda x: x['stats']['performance_stats']['win_rate'], 
                reverse=True
            )
        elif criteria == 'total_goals':
            teams_with_stats.sort(
                key=lambda x: x['stats']['goal_stats']['total_goals'], 
                reverse=True
            )
        elif criteria == 'total_tournaments':
            teams_with_stats.sort(
                key=lambda x: x['stats']['basic_stats']['total_tournaments'], 
                reverse=True
            )
        elif criteria == 'best_rank':
            # 最佳排名：数字越小越好，None排在最后
            teams_with_stats.sort(
                key=lambda x: (
                    x['stats']['performance_stats']['best_rank'] is None,
                    x['stats']['performance_stats']['best_rank'] or float('inf')
                )
            )
        
        return teams_with_stats[:limit]


# 导入datetime
from datetime import datetime

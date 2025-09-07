"""
TeamBase 统计服务
处理球队基础信息相关的数据查询和业务编排
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from app.models.team_base import TeamBase
from app.utils.team_utils import TeamUtils


class TeamBaseStatisticsService:
    """球队基础统计服务"""
    
    @staticmethod
    def calculate_team_historical_stats(team_base: TeamBase) -> Dict[str, Any]:
        """计算球队历史统计数据"""
        if not team_base.participations:
            return TeamUtils._get_empty_historical_stats()
        
        # 将参赛记录转换为字典格式传递给工具类
        participations_data = []
        for p in team_base.participations:
            participations_data.append({
                'tournament_goals': p.tournament_goals,
                'goals_conceded': p.goals_conceded,
                'points': p.points,
                'matches_played': p.matches_played,
                'wins': p.wins,
                'draws': p.draws,
                'losses': p.losses,
                'red_cards': p.red_cards,
                'yellow_cards': p.yellow_cards,
                'rank': p.rank
            })
        
        return TeamUtils.calculate_team_historical_metrics(participations_data)
    
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
        
        # 使用工具类进行排序
        sorted_teams = TeamUtils.sort_teams_by_performance_criteria(teams_with_stats, criteria)
        return sorted_teams[:limit]

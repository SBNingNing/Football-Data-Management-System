"""
足球统计服务类
处理球队参赛记录的数据查询和业务编排
"""

from typing import Dict, Any, List
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.models.tournament import Tournament
from app.models.team_base import TeamBase
from app.utils.stats_utils import StatsUtils
from app.database import db


class FootballStatisticsService:
    """足球统计服务类 - 处理数据查询和业务编排"""
    
    @staticmethod
    def calculate_team_participation_stats(participation: TeamTournamentParticipation) -> Dict[str, Any]:
        """计算球队参赛记录的统计数据"""
        participation_data = {
            'matches_played': participation.matches_played or 0,
            'wins': participation.wins or 0,
            'draws': participation.draws or 0,
            'losses': participation.losses or 0,
            'goals_for': participation.tournament_goals or 0,
            'goals_against': participation.tournament_goals_conceded or 0,
            'points': participation.tournament_points or 0,
            'rank': participation.tournament_rank,
            'red_cards': participation.tournament_red_cards or 0,
            'yellow_cards': participation.tournament_yellow_cards or 0
        }
        
        return StatsUtils.calculate_team_participation_metrics(participation_data)
    
    @staticmethod
    def get_team_tournament_ranking(tournament_id: int) -> List[Dict[str, Any]]:
        """获取赛事中所有球队的排名统计"""
        participations = TeamTournamentParticipation.query.filter_by(
            tournament_id=tournament_id,
            status='active'
        ).order_by(
            TeamTournamentParticipation.tournament_rank.asc()
        ).all()
        
        rankings = []
        for participation in participations:
            stats = FootballStatisticsService.calculate_team_participation_stats(participation)
            rankings.append({
                'team_id': participation.team_base_id,
                'team_name': participation.team_base.name if participation.team_base else None,
                'rank': participation.tournament_rank,
                'stats': stats
            })
        
        return rankings
    
    @staticmethod
    def compare_team_performances(team_base_id: int, tournament_ids: List[int]) -> Dict[str, Any]:
        """比较球队在不同赛事中的表现"""
        participations = TeamTournamentParticipation.query.filter(
            TeamTournamentParticipation.team_base_id == team_base_id,
            TeamTournamentParticipation.tournament_id.in_(tournament_ids),
            TeamTournamentParticipation.status == 'active'
        ).all()
        
        comparisons = []
        for participation in participations:
            stats = FootballStatisticsService.calculate_team_participation_stats(participation)
            tournament_name = participation.tournament.name if participation.tournament else 'Unknown'
            
            comparisons.append({
                'tournament_id': participation.tournament_id,
                'tournament_name': tournament_name,
                'stats': stats
            })
        
        return {
            'team_base_id': team_base_id,
            'comparisons': comparisons,
            'summary': StatsUtils.calculate_overall_tournament_summary([comp['stats'] for comp in comparisons])
        }

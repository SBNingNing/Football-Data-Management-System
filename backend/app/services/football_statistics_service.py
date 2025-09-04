"""
足球统计服务类
处理球队参赛记录的统计计算和分析
"""

from typing import Dict, Any, List
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.models.tournament import Tournament
from app.models.team_base import TeamBase
from app import db


class FootballStatisticsService:
    """足球统计服务类 - 处理各种足球相关的统计计算"""
    
    @staticmethod
    def calculate_team_participation_stats(participation: TeamTournamentParticipation) -> Dict[str, Any]:
        """计算球队参赛记录的统计数据"""
        
        # 基础统计
        matches_played = participation.matches_played or 0
        wins = participation.wins or 0
        draws = participation.draws or 0
        losses = participation.losses or 0
        
        # 进球统计
        goals_for = participation.tournament_goals or 0
        goals_against = participation.tournament_goals_conceded or 0
        goal_difference = participation.tournament_goal_difference or 0
        
        # 纪律统计
        red_cards = participation.tournament_red_cards or 0
        yellow_cards = participation.tournament_yellow_cards or 0
        
        # 积分和排名
        points = participation.tournament_points or 0
        rank = participation.tournament_rank
        
        return {
            'basic_stats': {
                'matches_played': matches_played,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'points': points,
                'rank': rank
            },
            'goal_stats': {
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goal_difference
            },
            'discipline_stats': {
                'red_cards': red_cards,
                'yellow_cards': yellow_cards
            },
            'calculated_stats': FootballStatisticsService._calculate_performance_metrics(
                matches_played, wins, draws, losses, goals_for, goals_against, goal_difference, points
            )
        }
    
    @staticmethod
    def _calculate_performance_metrics(matches_played: int, wins: int, draws: int, losses: int,
                                     goals_for: int, goals_against: int, goal_difference: int,
                                     points: int) -> Dict[str, float]:
        """计算性能指标"""
        if matches_played == 0:
            return {
                'win_rate': 0.0,
                'draw_rate': 0.0,
                'loss_rate': 0.0,
                'avg_goals_per_match': 0.0,
                'avg_goals_conceded_per_match': 0.0,
                'avg_goal_difference_per_match': 0.0,
                'points_per_match': 0.0
            }
        
        return {
            'win_rate': round((wins / matches_played) * 100, 2),
            'draw_rate': round((draws / matches_played) * 100, 2),
            'loss_rate': round((losses / matches_played) * 100, 2),
            'avg_goals_per_match': round(goals_for / matches_played, 2),
            'avg_goals_conceded_per_match': round(goals_against / matches_played, 2),
            'avg_goal_difference_per_match': round(goal_difference / matches_played, 2),
            'points_per_match': round(points / matches_played, 2)
        }
    
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
            'summary': FootballStatisticsService._calculate_overall_summary(comparisons)
        }
    
    @staticmethod
    def _calculate_overall_summary(comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算总体统计摘要"""
        if not comparisons:
            return {}
        
        total_matches = sum(comp['stats']['basic_stats']['matches_played'] for comp in comparisons)
        total_wins = sum(comp['stats']['basic_stats']['wins'] for comp in comparisons)
        total_draws = sum(comp['stats']['basic_stats']['draws'] for comp in comparisons)
        total_losses = sum(comp['stats']['basic_stats']['losses'] for comp in comparisons)
        total_goals_for = sum(comp['stats']['goal_stats']['goals_for'] for comp in comparisons)
        total_goals_against = sum(comp['stats']['goal_stats']['goals_against'] for comp in comparisons)
        total_points = sum(comp['stats']['basic_stats']['points'] for comp in comparisons)
        
        return {
            'total_tournaments': len(comparisons),
            'total_matches': total_matches,
            'total_wins': total_wins,
            'total_draws': total_draws,
            'total_losses': total_losses,
            'total_goals_for': total_goals_for,
            'total_goals_against': total_goals_against,
            'total_goal_difference': total_goals_for - total_goals_against,
            'total_points': total_points,
            'overall_performance': FootballStatisticsService._calculate_performance_metrics(
                total_matches, total_wins, total_draws, total_losses,
                total_goals_for, total_goals_against, total_goals_for - total_goals_against,
                total_points
            )
        }

"""
统计服务层 - 处理统计相关的业务逻辑
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, and_, case, or_

from app.database import db
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament
from app.models.event import Event
from app.models.player_team_history import PlayerTeamHistory
from app.models.player import Player
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StatsService:
    """统计业务逻辑服务类"""
    
    @staticmethod
    def get_match_statistics() -> Dict[str, int]:
        """获取比赛统计数据"""
        try:
            logger.info("开始获取比赛统计数据")
            
            # 使用复杂查询获取统计数据
            stats_query = db.session.query(
                func.count(Match.id).label('total'),
                func.sum(case((Match.status == 'F', 1), else_=0)).label('completed'),
                func.sum(case((Match.status.in_(['S', 'P']), 1), else_=0)).label('upcoming')
            ).first()
            
            # 处理查询结果
            if not stats_query:
                total_matches = completed_matches = upcoming_matches = 0
            else:
                total_matches = int(stats_query.total or 0)
                completed_matches = int(stats_query.completed or 0)
                upcoming_matches = int(stats_query.upcoming or 0)
            
            # 数据验证
            if total_matches < completed_matches + upcoming_matches:
                upcoming_matches = total_matches - completed_matches
            
            result = {
                'totalMatches': total_matches,
                'completedMatches': completed_matches,
                'upcomingMatches': max(0, upcoming_matches)
            }
            
            logger.info(f"成功获取比赛统计: {result}")
            return result
            
        except Exception as e:
            logger.warning(f"复杂查询失败，使用备用查询: {str(e)}")
            return StatsService._get_match_statistics_fallback()
    
    @staticmethod
    def _get_match_statistics_fallback() -> Dict[str, int]:
        """备用的比赛统计查询方法"""
        try:
            total_matches = Match.query.count()
            completed_matches = Match.query.filter_by(status='F').count()
            upcoming_matches = max(0, total_matches - completed_matches)
            
            result = {
                'totalMatches': total_matches,
                'completedMatches': completed_matches,
                'upcomingMatches': upcoming_matches
            }
            
            logger.info(f"备用查询成功: {result}")
            return result
            
        except Exception as e:
            logger.error(f"备用查询也失败: {str(e)}")
            raise
    
    @staticmethod
    def get_all_rankings() -> Dict[str, Any]:
        """获取所有赛事的排行榜数据"""
        try:
            logger.info("开始获取排行榜数据")
            
            tournaments = Tournament.query.all()
            rankings = {}
            
            for tournament in tournaments:
                tournament_key = StatsService._get_tournament_key(tournament.name)
                rankings[tournament_key] = StatsService._get_tournament_rankings(tournament)
            
            logger.info(f"成功获取 {len(rankings)} 个赛事的排行榜数据")
            return rankings
            
        except Exception as e:
            logger.error(f"获取排行榜数据失败: {str(e)}")
            raise
    
    @staticmethod
    def _get_tournament_rankings(tournament: Tournament) -> Dict[str, Any]:
        """获取单个赛事的排行榜数据"""
        try:
            # 获取各项排行数据
            player_goals = StatsService._get_top_scorers_players(tournament.id)
            team_goals = StatsService._get_top_scorers_teams(tournament.id)
            player_cards = StatsService._get_player_cards_stats(tournament.id)
            team_cards = StatsService._get_team_cards_stats(tournament.id)
            team_points = StatsService.calculate_team_points(tournament.id)
            
            return {
                'topScorers': {
                    'players': [
                        {
                            'id': player.player_id,
                            'name': player.player_name,
                            'team': player.team_name,
                            'goals': int(player.goals or 0)
                        } for player in player_goals
                    ],
                    'teams': [
                        {
                            'team': team.team_name,
                            'goals': int(team.goals or 0)
                        } for team in team_goals
                    ]
                },
                'cards': {
                    'players': [
                        {
                            'id': player.player_id,
                            'name': player.player_name,
                            'team': player.team_name,
                            'yellowCards': int(player.yellow_cards or 0),
                            'redCards': int(player.red_cards or 0)
                        } for player in player_cards
                    ],
                    'teams': [
                        {
                            'team': team.team_name,
                            'yellowCards': int(team.yellow_cards or 0),
                            'redCards': int(team.red_cards or 0)
                        } for team in team_cards
                    ]
                },
                'points': team_points
            }
            
        except Exception as e:
            logger.error(f"获取赛事 {tournament.name} 排行榜失败: {str(e)}")
            return {
                'topScorers': {'players': [], 'teams': []},
                'cards': {'players': [], 'teams': []},
                'points': []
            }
    
    @staticmethod
    def _get_top_scorers_players(tournament_id: int, limit: int = 5) -> List[Any]:
        """获取球员射手榜"""
        return db.session.query(
            PlayerTeamHistory.player_id,
            PlayerTeamHistory.player_name,
            PlayerTeamHistory.team_name,
            func.sum(PlayerTeamHistory.tournament_goals).label('goals')
        ).filter(
            and_(PlayerTeamHistory.tournament_id == tournament_id,
                 PlayerTeamHistory.tournament_goals > 0)
        ).group_by(
            PlayerTeamHistory.player_id,
            PlayerTeamHistory.player_name,
            PlayerTeamHistory.team_name
        ).order_by(
            func.sum(PlayerTeamHistory.tournament_goals).desc()
        ).limit(limit).all()
    
    @staticmethod
    def _get_top_scorers_teams(tournament_id: int, limit: int = 5) -> List[Any]:
        """获取球队射手榜"""
        return db.session.query(
            Team.team_name,
            func.sum(Team.tournament_goals).label('goals')
        ).filter(
            and_(Team.tournament_id == tournament_id,
                 Team.tournament_goals > 0)
        ).group_by(Team.team_name).order_by(
            func.sum(Team.tournament_goals).desc()
        ).limit(limit).all()
    
    @staticmethod
    def _get_player_cards_stats(tournament_id: int, limit: int = 5) -> List[Any]:
        """获取球员黄红牌统计"""
        return db.session.query(
            PlayerTeamHistory.player_id,
            PlayerTeamHistory.player_name,
            PlayerTeamHistory.team_name,
            func.sum(PlayerTeamHistory.tournament_yellow_cards).label('yellow_cards'),
            func.sum(PlayerTeamHistory.tournament_red_cards).label('red_cards')
        ).filter(
            and_(PlayerTeamHistory.tournament_id == tournament_id,
                 or_(PlayerTeamHistory.tournament_yellow_cards > 0,
                     PlayerTeamHistory.tournament_red_cards > 0))
        ).group_by(
            PlayerTeamHistory.player_id,
            PlayerTeamHistory.player_name,
            PlayerTeamHistory.team_name
        ).order_by(
            func.sum(PlayerTeamHistory.tournament_red_cards).desc(),
            func.sum(PlayerTeamHistory.tournament_yellow_cards).desc()
        ).limit(limit).all()
    
    @staticmethod
    def _get_team_cards_stats(tournament_id: int, limit: int = 5) -> List[Any]:
        """获取球队黄红牌统计"""
        return db.session.query(
            Team.team_name,
            func.sum(Team.tournament_yellow_cards).label('yellow_cards'),
            func.sum(Team.tournament_red_cards).label('red_cards')
        ).filter(
            and_(Team.tournament_id == tournament_id,
                 or_(Team.tournament_yellow_cards > 0,
                     Team.tournament_red_cards > 0))
        ).group_by(Team.team_name).order_by(
            func.sum(Team.tournament_red_cards).desc(),
            func.sum(Team.tournament_yellow_cards).desc()
        ).limit(limit).all()
    
    @staticmethod
    def calculate_team_points(tournament_id: int) -> List[Dict[str, Any]]:
        """计算球队积分榜"""
        try:
            logger.info(f"开始计算赛事 {tournament_id} 的积分榜")
            
            # 获取积分榜数据
            team_points = db.session.query(
                Team.team_name,
                Team.tournament_points.label('points'),
                Team.tournament_goals.label('goals_for'),
                Team.tournament_goals_against.label('goals_against'),
                Team.tournament_goal_difference.label('goal_difference'),
                func.row_number().over(
                    order_by=[
                        Team.tournament_points.desc(),
                        Team.tournament_goal_difference.desc(),
                        Team.tournament_goals.desc()
                    ]
                ).label('rank')
            ).filter(
                Team.tournament_id == tournament_id
            ).order_by(
                Team.tournament_points.desc(),
                Team.tournament_goal_difference.desc(),
                Team.tournament_goals.desc()
            ).limit(10).all()
            
            # 格式化结果
            results = []
            for team_data in team_points:
                matches_played = StatsService._get_team_matches_played(
                    tournament_id, team_data.team_name
                )
                
                results.append({
                    'team': team_data.team_name,
                    'matchesPlayed': matches_played,
                    'points': int(team_data.points or 0),
                    'goalsFor': int(team_data.goals_for or 0),
                    'goalsAgainst': int(team_data.goals_against or 0),
                    'goalDifference': int(team_data.goal_difference or 0),
                    'rank': team_data.rank
                })
            
            logger.info(f"成功计算积分榜，包含 {len(results)} 支球队")
            return results
            
        except Exception as e:
            logger.error(f"计算积分榜失败: {str(e)}")
            return []
    
    @staticmethod
    def _get_team_matches_played(tournament_id: int, team_name: str) -> int:
        """获取球队已踢比赛场次"""
        try:
            team = Team.query.filter_by(
                name=team_name, 
                tournament_id=tournament_id
            ).first()
            
            if not team:
                return 0
            
            matches_played = Match.query.filter(
                and_(
                    Match.tournament_id == tournament_id,
                    or_(Match.home_team_id == team.id,
                        Match.away_team_id == team.id),
                    Match.status == 'F'
                )
            ).count()
            
            return matches_played
            
        except Exception as e:
            logger.warning(f"获取球队 {team_name} 比赛场次失败: {str(e)}")
            return 0
    
    @staticmethod
    def _get_tournament_key(tournament_name: str) -> str:
        """生成赛事key"""
        return tournament_name.lower().replace(' ', '_').replace('-', '_')
    
    @staticmethod
    def get_tournament_statistics(tournament_id: int) -> Dict[str, Any]:
        """获取单个赛事的详细统计"""
        try:
            logger.info(f"开始获取赛事 {tournament_id} 的详细统计")
            
            tournament = Tournament.query.get_or_404(tournament_id)
            
            # 比赛统计
            total_matches = Match.query.filter_by(tournament_id=tournament_id).count()
            completed_matches = Match.query.filter_by(
                tournament_id=tournament_id, status='F'
            ).count()
            
            # 球队统计
            total_teams = Team.query.filter_by(tournament_id=tournament_id).count()
            
            # 总进球数
            total_goals = db.session.query(
                func.sum(Team.tournament_goals)
            ).filter_by(tournament_id=tournament_id).scalar() or 0
            
            # 平均每场进球
            avg_goals_per_match = (
                total_goals / completed_matches if completed_matches > 0 else 0
            )
            
            result = {
                'tournament': {
                    'id': tournament.id,
                    'name': tournament.name
                },
                'matches': {
                    'total': total_matches,
                    'completed': completed_matches,
                    'remaining': total_matches - completed_matches
                },
                'teams': {
                    'total': total_teams
                },
                'goals': {
                    'total': int(total_goals),
                    'average_per_match': round(avg_goals_per_match, 2)
                }
            }
            
            logger.info(f"成功获取赛事统计: {result}")
            return result
            
        except Exception as e:
            logger.error(f"获取赛事统计失败: {str(e)}")
            raise

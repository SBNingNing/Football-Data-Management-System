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
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.models.team_base import TeamBase
from app.models.competition import Competition
from app.models.season import Season
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
            
            # 获取球队和球员总数
            total_teams = TeamBase.query.count()
            total_players = Player.query.count()
            
            result = {
                'totalMatches': total_matches,
                'completedMatches': completed_matches,
                'upcomingMatches': max(0, upcoming_matches),
                'totalTeams': total_teams,
                'totalPlayers': total_players
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
            
            total_teams = TeamBase.query.count()
            total_players = Player.query.count()
            
            result = {
                'totalMatches': total_matches,
                'completedMatches': completed_matches,
                'upcomingMatches': upcoming_matches,
                'totalTeams': total_teams,
                'totalPlayers': total_players
            }
            
            logger.info(f"备用查询成功: {result}")
            return result
            
        except Exception as e:
            logger.error(f"备用查询也失败: {str(e)}")
            raise
    
    @staticmethod
    def get_all_rankings(season_id: int = None) -> Dict[str, Any]:
        """获取所有赛事的排行榜数据"""
        try:
            logger.info(f"开始获取排行榜数据, season_id={season_id}")
            
            competitions = Competition.query.all()
            rankings = {}
            
            for comp in competitions:
                # 构建基础查询
                query = Tournament.query.join(Season).filter(Tournament.competition_id == comp.competition_id)
                
                target_tournaments = []
                if season_id:
                    # 如果指定了赛季，获取该赛季的所有赛事
                    target_tournaments = query.filter(Tournament.season_id == season_id).all()
                else:
                    # 否则获取最新的赛事（可能需要定义什么是"最新"，这里假设是最近一个赛季的所有赛事）
                    # 先找到最近的赛季ID
                    latest_season = Season.query.order_by(Season.start_time.desc()).first()
                    if latest_season:
                        target_tournaments = query.filter(Tournament.season_id == latest_season.id).all()
                
                key = f"comp_{comp.competition_id}"
                if target_tournaments:
                    # 聚合所有相关赛事的排行数据
                    rankings[key] = StatsService._get_aggregated_rankings(target_tournaments)
                    # 附加元数据
                    rankings[key]['competitionName'] = comp.name
                    # 使用第一个赛事的赛季名称
                    rankings[key]['seasonName'] = target_tournaments[0].season.name if target_tournaments[0].season else ''
                else:
                    rankings[key] = {
                        'topScorers': {'players': [], 'teams': []},
                        'cards': {'players': [], 'teams': []},
                        'points': [],
                        'competitionName': comp.name,
                        'seasonName': ''
                    }
            
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
                            'goals': int(team.goals or 0),
                            'goalsConceded': int(team.goals_conceded or 0),
                            'goalDifference': int(team.goal_difference or 0)
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
    def _get_aggregated_rankings(tournaments: List[Tournament]) -> Dict[str, Any]:
        """获取聚合的排行榜数据（支持多个赛事）"""
        try:
            tournament_ids = [t.id for t in tournaments]
            if not tournament_ids:
                return {
                    'topScorers': {'players': [], 'teams': []},
                    'cards': {'players': [], 'teams': []},
                    'points': []
                }

            # 获取各项排行数据
            player_goals = StatsService._get_top_scorers_players(tournament_ids)
            team_goals = StatsService._get_top_scorers_teams(tournament_ids)
            player_cards = StatsService._get_player_cards_stats(tournament_ids)
            team_cards = StatsService._get_team_cards_stats(tournament_ids)
            # 积分榜通常按赛事独立计算，聚合可能比较复杂，这里暂时只取第一个赛事的积分榜，或者需要重新计算
            # 如果是同一赛季的多个阶段（如小组赛+淘汰赛），积分榜可能只针对小组赛
            # 这里简单处理：合并所有赛事的积分榜，或者只取第一个
            # 为了准确性，我们尝试聚合所有赛事的积分（如果有意义的话）
            # 但通常积分榜是针对特定赛制的。这里我们假设取第一个赛事的积分榜作为展示，或者重新计算
            # 考虑到 TeamService 是聚合的，这里也尝试聚合
            team_points = StatsService._calculate_aggregated_team_points(tournament_ids)
            
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
                            'goals': int(team.goals or 0),
                            'goalsConceded': int(team.goals_conceded or 0),
                            'goalDifference': int(team.goal_difference or 0)
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
            logger.error(f"获取聚合排行榜失败: {str(e)}")
            return {
                'topScorers': {'players': [], 'teams': []},
                'cards': {'players': [], 'teams': []},
                'points': []
            }

    @staticmethod
    def _get_top_scorers_players(tournament_ids: List[int], limit: int = 5) -> List[Any]:
        """获取球员射手榜"""
        return (
            db.session.query(
                PlayerTeamHistory.player_id,
                Player.name.label('player_name'),
                TeamBase.name.label('team_name'),
                func.sum(PlayerTeamHistory.tournament_goals).label('goals')
            )
            .join(Player, PlayerTeamHistory.player_id == Player.id)
            .outerjoin(TeamTournamentParticipation, PlayerTeamHistory.team_id == TeamTournamentParticipation.id)
            .outerjoin(TeamBase, TeamTournamentParticipation.team_base_id == TeamBase.id)
            .filter(
                and_(
                    PlayerTeamHistory.tournament_id.in_(tournament_ids),
                    PlayerTeamHistory.tournament_goals > 0
                )
            )
            .group_by(
                PlayerTeamHistory.player_id,
                Player.name,
                TeamBase.name
            )
            .order_by(func.sum(PlayerTeamHistory.tournament_goals).desc())
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def _get_top_scorers_teams(tournament_ids: List[int], limit: int = 5) -> List[Any]:
        """获取球队射手榜"""
        return (
            db.session.query(
                Team.name.label('team_name'),
                func.sum(Team.tournament_goals).label('goals'),
                func.sum(Team.tournament_goals_conceded).label('goals_conceded'),
                func.sum(Team.tournament_goal_difference).label('goal_difference')
            )
            .filter(
                and_(
                    Team.tournament_id.in_(tournament_ids),
                    Team.tournament_goals > 0
                )
            )
            .group_by(Team.name)
            .order_by(func.sum(Team.tournament_goals).desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def _get_player_cards_stats(tournament_ids: List[int], limit: int = 5) -> List[Any]:
        """获取球员红黄牌榜"""
        return (
            db.session.query(
                PlayerTeamHistory.player_id,
                Player.name.label('player_name'),
                TeamBase.name.label('team_name'),
                func.sum(PlayerTeamHistory.tournament_yellow_cards).label('yellow_cards'),
                func.sum(PlayerTeamHistory.tournament_red_cards).label('red_cards')
            )
            .join(Player, PlayerTeamHistory.player_id == Player.id)
            .outerjoin(TeamTournamentParticipation, PlayerTeamHistory.team_id == TeamTournamentParticipation.id)
            .outerjoin(TeamBase, TeamTournamentParticipation.team_base_id == TeamBase.id)
            .filter(
                and_(
                    PlayerTeamHistory.tournament_id.in_(tournament_ids),
                    or_(
                        PlayerTeamHistory.tournament_yellow_cards > 0,
                        PlayerTeamHistory.tournament_red_cards > 0
                    )
                )
            )
            .group_by(
                PlayerTeamHistory.player_id,
                Player.name,
                TeamBase.name
            )
            .order_by(
                func.sum(PlayerTeamHistory.tournament_red_cards).desc(),
                func.sum(PlayerTeamHistory.tournament_yellow_cards).desc()
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def _get_team_cards_stats(tournament_ids: List[int], limit: int = 5) -> List[Any]:
        """获取球队红黄牌榜"""
        return (
            db.session.query(
                Team.name.label('team_name'),
                func.sum(Team.tournament_yellow_cards).label('yellow_cards'),
                func.sum(Team.tournament_red_cards).label('red_cards')
            )
            .filter(
                and_(
                    Team.tournament_id.in_(tournament_ids),
                    or_(
                        Team.tournament_yellow_cards > 0,
                        Team.tournament_red_cards > 0
                    )
                )
            )
            .group_by(Team.name)
            .order_by(
                func.sum(Team.tournament_red_cards).desc(),
                func.sum(Team.tournament_yellow_cards).desc()
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def _calculate_aggregated_team_points(tournament_ids: List[int]) -> List[Dict[str, Any]]:
        """计算聚合的球队积分榜"""
        teams = (
            db.session.query(
                Team.name.label('team_name'),
                func.sum(Team.matches_played).label('matches_played'),
                func.sum(Team.tournament_points).label('points'),
                func.sum(Team.tournament_goals).label('goals'),
                func.sum(Team.tournament_goals_conceded).label('goals_conceded'),
                func.sum(Team.tournament_goal_difference).label('goal_difference')
            )
            .filter(Team.tournament_id.in_(tournament_ids))
            .group_by(Team.name)
            .order_by(
                func.sum(Team.tournament_points).desc(),
                func.sum(Team.tournament_goal_difference).desc(),
                func.sum(Team.tournament_goals).desc()
            )
            .all()
        )
        
        return [
            {
                'team': team.team_name,
                'matchesPlayed': int(team.matches_played or 0),
                'points': int(team.points or 0),
                'goals': int(team.goals or 0),
                'goalsConceded': int(team.goals_conceded or 0),
                'goalDifference': int(team.goal_difference or 0)
            } for team in teams
        ]
    
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

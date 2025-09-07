"""
球队服务层 - 处理球队相关业务逻辑
"""
from typing import Dict, List, Any, Optional, Tuple
from app.database import db
from app.models.team import Team
from app.models.team_base import TeamBase
from app.models.team_tournament_participation import TeamTournamentParticipation
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class TeamService:
    """球队业务服务类"""
    
    @staticmethod
    def get_team_by_name_new_api(team_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """使用新架构根据球队名称获取统计信息"""
        try:
            team_base = TeamBase.query.filter_by(name=team_name).first()
            if not team_base:
                return None, '球队不存在'
            
            participations = TeamTournamentParticipation.query.filter_by(team_base_id=team_base.id).all()
            if not participations:
                return None, '未找到球队参赛记录'
            
            historical_stats = team_base.get_historical_stats()
            
            team_info = {
                'teamName': team_name,
                'totalGoals': historical_stats['total_goals'],
                'totalGoalsConceded': historical_stats['total_goals_conceded'],
                'totalGoalDifference': historical_stats['total_goal_difference'],
                'totalRedCards': historical_stats['total_red_cards'],
                'totalYellowCards': historical_stats['total_yellow_cards'],
                'totalPoints': historical_stats['total_points'],
                'totalMatchesPlayed': historical_stats['total_matches_played'],
                'totalWins': historical_stats['total_wins'],
                'totalDraws': historical_stats['total_draws'],
                'totalLosses': historical_stats['total_losses'],
                'bestRank': historical_stats['best_rank'],
                'winRate': historical_stats['win_rate'],
                'records': []
            }
            
            for participation in participations:
                team_record = Team.query.filter_by(
                    tournament_id=participation.tournament_id,
                    team_base_id=team_base.id
                ).first()
                
                record_dict = {
                    'id': participation.id,
                    'teamName': team_name,
                    'tournament_id': participation.tournament_id,
                    'tournament_name': participation.tournament.name if participation.tournament else None,
                    'season_name': participation.tournament.season.name if participation.tournament and participation.tournament.season else None,
                    'competition_name': participation.tournament.competition.name if participation.tournament and participation.tournament.competition else None,
                    'rank': participation.rank,
                    'goals': participation.goals,
                    'goalsConceded': participation.goals_conceded,
                    'goalDifference': participation.goal_difference,
                    'redCards': participation.red_cards,
                    'yellowCards': participation.yellow_cards,
                    'points': participation.points,
                    'matchesPlayed': participation.matches_played,
                    'wins': participation.wins,
                    'draws': participation.draws,
                    'losses': participation.losses
                }
                
                team_players = []
                if team_record:
                    player_histories = PlayerTeamHistory.query.filter_by(
                        team_id=team_record.id, 
                        tournament_id=participation.tournament_id
                    ).all()
                    
                    for history in player_histories:
                        if history.player:
                            team_players.append({
                                'name': history.player.name,
                                'playerId': history.player_id,
                                'studentId': history.player_id,
                                'id': history.player_id,
                                'number': str(history.player_number),
                                'goals': history.tournament_goals,
                                'redCards': history.tournament_red_cards,
                                'yellowCards': history.tournament_yellow_cards
                            })
                
                record_dict['players'] = team_players
                team_info['records'].append(record_dict)
            
            return team_info, None
            
        except Exception as e:
            logger.error(f"Error getting team by name (new API): {e}")
            return None, str(e)
    
    @staticmethod
    def get_team_by_name(team_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """根据球队名称获取统计信息和历史记录"""
        try:
            team_records = Team.query.filter_by(name=team_name).all()
            if not team_records:
                return None, '球队不存在'
            
            # 统计总数据
            total_goals = sum(record.tournament_goals for record in team_records)
            total_goals_conceded = sum(record.tournament_goals_conceded for record in team_records)
            total_goal_difference = sum(record.tournament_goal_difference for record in team_records)
            total_red_cards = sum(record.tournament_red_cards for record in team_records)
            total_yellow_cards = sum(record.tournament_yellow_cards for record in team_records)
            total_points = sum(record.tournament_points for record in team_records)
            total_matches_played = sum(record.matches_played for record in team_records)
            total_wins = sum(record.wins for record in team_records)
            total_draws = sum(record.draws for record in team_records)
            total_losses = sum(record.losses for record in team_records)
            
            valid_ranks = [record.tournament_rank for record in team_records if record.tournament_rank and record.tournament_rank > 0]
            best_rank = min(valid_ranks) if valid_ranks else None
            
            team_info = {
                'teamName': team_name,
                'totalGoals': total_goals,
                'totalGoalsConceded': total_goals_conceded,
                'totalGoalDifference': total_goal_difference,
                'totalRedCards': total_red_cards,
                'totalYellowCards': total_yellow_cards,
                'totalPoints': total_points,
                'totalMatchesPlayed': total_matches_played,
                'totalWins': total_wins,
                'totalDraws': total_draws,
                'totalLosses': total_losses,
                'bestRank': best_rank,
                'records': []
            }
            
            for record in team_records:
                record_dict = record.to_dict()
                record_dict['teamName'] = record_dict['name']
                
                team_players = []
                player_histories = PlayerTeamHistory.query.filter_by(
                    team_id=record.id, 
                    tournament_id=record.tournament_id
                ).all()
                
                for history in player_histories:
                    team_players.append({
                        'name': history.player.name,
                        'playerId': history.player_id,
                        'studentId': history.player_id,
                        'id': history.player_id,
                        'number': str(history.player_number),
                        'goals': history.tournament_goals,
                        'redCards': history.tournament_red_cards,
                        'yellowCards': history.tournament_yellow_cards
                    })
                
                record_dict['players'] = team_players
                record_dict.update({
                    'rank': record.tournament_rank,
                    'goals': record.tournament_goals,
                    'goalsConceded': record.tournament_goals_conceded,
                    'goalDifference': record.tournament_goal_difference,
                    'redCards': record.tournament_red_cards,
                    'yellowCards': record.tournament_yellow_cards,
                    'points': record.tournament_points,
                    'tournamentId': record.tournament_id,
                    'tournamentName': record.tournament.name if record.tournament else None
                })
                
                team_info['records'].append(record_dict)
            
            return team_info, None
            
        except Exception as e:
            logger.error(f"Error getting team by name: {e}")
            return None, f'获取失败: {str(e)}'
    
    @staticmethod
    def get_all_teams(group_by_name: bool = False) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """获取所有球队信息"""
        try:
            if group_by_name:
                teams = Team.query.all()
                teams_grouped = {}
                
                for team in teams:
                    team_name = team.name
                    if team_name not in teams_grouped:
                        teams_grouped[team_name] = {
                            'teamName': team_name,
                            'totalGoals': 0,
                            'totalGoalsConceded': 0,
                            'totalGoalDifference': 0,
                            'totalRedCards': 0,
                            'totalYellowCards': 0,
                            'totalPoints': 0,
                            'bestRank': None,
                            'tournaments': []
                        }
                    
                    teams_grouped[team_name]['totalGoals'] += team.tournament_goals
                    teams_grouped[team_name]['totalGoalsConceded'] += team.tournament_goals_conceded
                    teams_grouped[team_name]['totalGoalDifference'] += team.tournament_goal_difference
                    teams_grouped[team_name]['totalRedCards'] += team.tournament_red_cards
                    teams_grouped[team_name]['totalYellowCards'] += team.tournament_yellow_cards
                    teams_grouped[team_name]['totalPoints'] += team.tournament_points
                    
                    if team.tournament_rank and team.tournament_rank > 0:
                        current_best = teams_grouped[team_name]['bestRank']
                        if current_best is None or team.tournament_rank < current_best:
                            teams_grouped[team_name]['bestRank'] = team.tournament_rank
                    
                    teams_grouped[team_name]['tournaments'].append({
                        'tournamentId': team.tournament_id,
                        'tournamentName': team.tournament.name if team.tournament else None
                    })
                
                return list(teams_grouped.values()), None
            else:
                teams = Team.query.all()
                teams_data = []
                
                for team in teams:
                    team_players = []
                    player_histories = PlayerTeamHistory.query.filter_by(
                        team_id=team.id, 
                        tournament_id=team.tournament_id
                    ).all()
                    
                    for history in player_histories:
                        team_players.append({
                            'name': history.player.name,
                            'playerId': history.player_id,
                            'studentId': history.player_id,
                            'id': history.player_id,
                            'number': str(history.player_number),
                            'goals': history.tournament_goals,
                            'redCards': history.tournament_red_cards,
                            'yellowCards': history.tournament_yellow_cards
                        })
                    
                    standardized_team = {
                        'id': team.id,
                        'teamName': team.name,
                        'name': team.name,
                        'tournamentId': team.tournament_id,
                        'tournamentName': team.tournament.name if team.tournament else None,
                        'groupId': team.group_id,
                        'rank': team.tournament_rank,
                        'goals': team.tournament_goals,
                        'goalsConceded': team.tournament_goals_conceded,
                        'goalDifference': team.tournament_goal_difference,
                        'redCards': team.tournament_red_cards,
                        'yellowCards': team.tournament_yellow_cards,
                        'points': team.tournament_points,
                        'players': team_players,
                        'createdAt': team.created_at.isoformat() if hasattr(team, 'created_at') and team.created_at else None
                    }
                    
                    teams_data.append(standardized_team)
                
                return teams_data, None
                
        except Exception as e:
            logger.error(f"Error getting all teams: {e}")
            return None, f'获取失败: {str(e)}'
    
    @staticmethod
    def create_team(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """创建球队和球员信息"""
        try:
            match_type_to_tournament = {
                'champions-cup': 1,
                'womens-cup': 2,
                'eight-a-side': 3
            }
            tournament_id = match_type_to_tournament.get(data.get('matchType', 'champions-cup'), 1)
            
            existing_team = Team.query.filter_by(name=data['teamName'], tournament_id=tournament_id).first()
            if existing_team:
                return None, '该赛事中球队名称已存在'
            
            new_team = Team(
                name=data['teamName'],
                tournament_id=tournament_id,
                group_id=data.get('groupId')
            )
            db.session.add(new_team)
            db.session.flush()
            
            players_data = data.get('players', [])
            for player_data in players_data:
                if player_data.get('name') and player_data.get('studentId'):
                    player_id = player_data['studentId']
                    
                    existing_player = Player.query.get(player_id)
                    if not existing_player:
                        new_player = Player(
                            id=player_id,
                            name=player_data['name']
                        )
                        db.session.add(new_player)
                    else:
                        existing_player.name = player_data['name']
                    
                    player_history = PlayerTeamHistory(
                        player_id=player_id,
                        player_number=int(player_data.get('number', 1)),
                        team_id=new_team.id,
                        tournament_id=tournament_id
                    )
                    db.session.add(player_history)
            
            db.session.commit()
            return TeamService._build_team_response(new_team), None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating team: {e}")
            return None, f'创建失败: {str(e)}'
    
    @staticmethod
    def update_team(team_id: int, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """更新球队信息"""
        try:
            team = Team.query.get(team_id)
            if not team:
                return None, '球队不存在'
            
            old_tournament_id = team.tournament_id
            
            if data.get('teamName'):
                team.name = data['teamName']
            
            if data.get('matchType'):
                match_type_to_tournament = {
                    'champions-cup': 1,
                    'womens-cup': 2,
                    'eight-a-side': 3
                }
                new_tournament_id = match_type_to_tournament.get(data['matchType'], 1)
                
                if new_tournament_id != old_tournament_id:
                    existing_team = Team.query.filter_by(
                        name=team.name, 
                        tournament_id=new_tournament_id
                    ).filter(Team.id != team_id).first()
                    
                    if existing_team:
                        return None, '目标赛事中已存在同名球队'
                    
                    team.tournament_id = new_tournament_id
            
            PlayerTeamHistory.query.filter_by(team_id=team_id, tournament_id=old_tournament_id).delete()
            if team.tournament_id != old_tournament_id:
                PlayerTeamHistory.query.filter_by(team_id=team_id, tournament_id=team.tournament_id).delete()
            
            players_data = data.get('players', [])
            for player_data in players_data:
                if player_data.get('name') and player_data.get('studentId'):
                    player_id = player_data['studentId']
                    
                    existing_player = Player.query.get(player_id)
                    if not existing_player:
                        new_player = Player(
                            id=player_id,
                            name=player_data['name']
                        )
                        db.session.add(new_player)
                    else:
                        existing_player.name = player_data['name']
                    
                    player_history = PlayerTeamHistory(
                        player_id=player_id,
                        player_number=int(player_data.get('number', 1)),
                        team_id=team_id,
                        tournament_id=team.tournament_id
                    )
                    db.session.add(player_history)
            
            db.session.commit()
            return TeamService._build_team_response(team), None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating team: {e}")
            return None, f'更新失败: {str(e)}'
    
    @staticmethod
    def delete_team(team_id: int) -> Tuple[bool, Optional[str]]:
        """删除球队"""
        try:
            team = Team.query.get(team_id)
            if not team:
                return False, '球队不存在'

            db.session.delete(team)
            db.session.commit()
            
            logger.info(f"Team deleted successfully: {team_id}")
            return True, None

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting team: {e}")
            return False, f'删除失败: {str(e)}'
    
    @staticmethod
    def _build_team_response(team: Team) -> Dict[str, Any]:
        """构建球队响应数据"""
        team_dict = team.to_dict()
        team_dict['teamName'] = team_dict['name']
        
        team_players = []
        for history in PlayerTeamHistory.query.filter_by(team_id=team.id, tournament_id=team.tournament_id).all():
            team_players.append({
                'name': history.player.name,
                'playerId': history.player_id,
                'studentId': history.player_id,
                'id': history.player_id,
                'number': str(history.player_number),
                'goals': history.tournament_goals,
                'redCards': history.tournament_red_cards,
                'yellowCards': history.tournament_yellow_cards
            })
        
        team_dict['players'] = team_players
        team_dict.update({
            'rank': team.tournament_rank,
            'goals': team.tournament_goals,
            'goalsConceded': team.tournament_goals_conceded,
            'goalDifference': team.tournament_goal_difference,
            'redCards': team.tournament_red_cards,
            'yellowCards': team.tournament_yellow_cards,
            'points': team.tournament_points,
            'tournamentId': team.tournament_id,
            'tournamentName': team.tournament.name if team.tournament else None
        })
        
        return team_dict

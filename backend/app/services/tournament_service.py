"""
赛事服务层 - 处理赛事相关业务逻辑
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import urllib.parse
from sqlalchemy import text

from app.database import db
from app.models.tournament import Tournament
from app.models.competition import Competition
from app.models.season import Season
from app.models.team import Team
from app.models.player_team_history import PlayerTeamHistory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TournamentService:
    """赛事服务类"""
    
    @staticmethod
    def find_tournament_by_name(tournament_name: str) -> Tuple[List[Tournament], List[str]]:
        """根据赛事名称查找赛事"""
        decoded_name = urllib.parse.unquote(tournament_name, encoding='utf-8').strip()
        
        all_tournaments = Tournament.query.all()
        all_names = [t.name for t in all_tournaments]
        
        # 精确匹配
        tournament_records = Tournament.query.filter(Tournament.name == decoded_name).all()
        
        # 模糊匹配
        if not tournament_records:
            tournament_records = Tournament.query.filter(
                Tournament.name.like(f"%{decoded_name}%")
            ).all()
        
        # 忽略大小写匹配
        if not tournament_records:
            tournament_records = Tournament.query.filter(
                Tournament.name.ilike(f"%{decoded_name}%")
            ).all()
        
        return tournament_records, all_names
    
    @staticmethod
    def get_tournament_teams_data(tournament_id: int) -> List[Dict[str, Any]]:
        """获取赛事下的所有球队数据"""
        tournament_teams = Team.query.filter(Team.tournament_id == tournament_id).all()
        teams_data = []
        
        for team in tournament_teams:
            team_players = PlayerTeamHistory.query.filter(
                PlayerTeamHistory.team_id == team.id,
                PlayerTeamHistory.tournament_id == tournament_id
            ).all()
            
            players_data = []
            for player_history in team_players:
                try:
                    player_dict = {
                        'player_id': player_history.player_id,
                        'player_name': player_history.player.name if hasattr(player_history, 'player') and player_history.player else f'球员{player_history.player_id}',
                        'player_number': player_history.player_number,
                        'goals': player_history.tournament_goals or 0,
                        'redCards': player_history.tournament_red_cards or 0,
                        'yellowCards': player_history.tournament_yellow_cards or 0,
                        'remarks': player_history.remarks or ''
                    }
                    players_data.append(player_dict)
                except Exception as player_error:
                    logger.error(f"处理球员数据失败: {player_error}")
                    continue
            
            team_dict = {
                'id': team.id,
                'name': team.name or '',
                'goals': team.tournament_goals or 0,
                'goalsConceded': team.tournament_goals_conceded or 0,
                'goalDifference': team.tournament_goal_difference or 0,
                'points': team.tournament_points or 0,
                'rank': team.tournament_rank or 0,
                'redCards': team.tournament_red_cards or 0,
                'yellowCards': team.tournament_yellow_cards or 0,
                'groupId': team.group_id,
                'players': players_data,
                'playerCount': len(players_data)
            }
            teams_data.append(team_dict)
        
        return teams_data
    
    @staticmethod
    def build_tournament_record_dict(tournament: Tournament, teams_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建赛事记录字典"""
        total_goals = sum(team_data['goals'] for team_data in teams_data)
        
        season_start_time = None
        season_end_time = None
        
        if tournament.season_start_time:
            try:
                season_start_time = tournament.season_start_time.isoformat()
            except:
                season_start_time = str(tournament.season_start_time)
        
        if tournament.season_end_time:
            try:
                season_end_time = tournament.season_end_time.isoformat()
            except:
                season_end_time = str(tournament.season_end_time)
        
        return {
            'id': tournament.id,
            'name': tournament.name,
            'tournamentName': tournament.name,
            'teams': teams_data,
            'teamCount': len(teams_data),
            'totalGoals': total_goals,
            'totalTeams': len(teams_data),
            'seasonStartTime': season_start_time,
            'seasonEndTime': season_end_time,
            'isGrouped': tournament.is_grouped or False,
            'seasonName': tournament.season_name or tournament.name
        }
    
    @staticmethod
    def get_tournament_info_by_name(tournament_name: str) -> Dict[str, Any]:
        """根据赛事名称获取完整赛事信息"""
        tournament_records, all_names = TournamentService.find_tournament_by_name(tournament_name)
        
        if not tournament_records:
            decoded_name = urllib.parse.unquote(tournament_name, encoding='utf-8').strip()
            raise ValueError(f'赛事"{decoded_name}"不存在')
        
        tournament_info = {
            'tournamentName': urllib.parse.unquote(tournament_name, encoding='utf-8').strip(),
            'totalSeasons': len(tournament_records),
            'records': []
        }
        
        for record in tournament_records:
            try:
                teams_data = TournamentService.get_tournament_teams_data(record.id)
                record_dict = TournamentService.build_tournament_record_dict(record, teams_data)
                tournament_info['records'].append(record_dict)
            except Exception as record_error:
                logger.error(f"处理赛事记录失败: {record_error}")
                continue
        
        return tournament_info
    
    @staticmethod
    def get_all_tournaments(group_by_name: bool = False) -> List[Dict[str, Any]]:
        """获取所有赛事信息"""
        tournaments = Tournament.query.all()
        
        if not tournaments:
            return []
        
        if group_by_name:
            return TournamentService._get_tournaments_grouped_by_name(tournaments)
        else:
            return TournamentService._get_all_tournaments_detailed(tournaments)
    
    @staticmethod
    def _get_tournaments_grouped_by_name(tournaments: List[Tournament]) -> List[Dict[str, Any]]:
        """按名称分组获取赛事信息"""
        tournaments_grouped = {}
        
        for tournament in tournaments:
            tournament_name = tournament.name
            if tournament_name not in tournaments_grouped:
                tournaments_grouped[tournament_name] = {
                    'tournamentName': tournament_name,
                    'totalSeasons': 0,
                    'totalTeams': 0,
                    'totalGoals': 0,
                    'seasons': []
                }
            
            tournament_teams = Team.query.filter(Team.tournament_id == tournament.id).all()
            total_goals = sum(team.tournament_goals or 0 for team in tournament_teams)
            
            tournaments_grouped[tournament_name]['totalSeasons'] += 1
            tournaments_grouped[tournament_name]['totalTeams'] += len(tournament_teams)
            tournaments_grouped[tournament_name]['totalGoals'] += total_goals
            
            season_info = {
                'tournament_id': tournament.id,
                'season_name': tournament.season_name or '',
                'is_grouped': tournament.is_grouped or False,
                'team_count': len(tournament_teams),
                'total_goals': total_goals
            }
            
            try:
                if tournament.season_start_time:
                    season_info['season_start_time'] = tournament.season_start_time.isoformat()
                else:
                    season_info['season_start_time'] = None
                    
                if tournament.season_end_time:
                    season_info['season_end_time'] = tournament.season_end_time.isoformat()
                else:
                    season_info['season_end_time'] = None
            except Exception:
                season_info['season_start_time'] = None
                season_info['season_end_time'] = None
            
            tournaments_grouped[tournament_name]['seasons'].append(season_info)
        
        return list(tournaments_grouped.values())
    
    @staticmethod
    def _get_all_tournaments_detailed(tournaments: List[Tournament]) -> List[Dict[str, Any]]:
        """获取所有赛事的详细信息"""
        tournaments_data = []
        
        for tournament in tournaments:
            try:
                teams_data = TournamentService.get_tournament_teams_data(tournament.id)
                tournament_dict = TournamentService.build_tournament_record_dict(tournament, teams_data)
                tournaments_data.append(tournament_dict)
            except Exception as tournament_error:
                logger.error(f"处理赛事数据失败: {tournament_error}")
                continue
        
        return tournaments_data
    
    @staticmethod
    def create_tournament(data: Dict[str, Any]) -> Tournament:
        """创建赛事"""
        season_start_time = datetime.fromisoformat(data['season_start_time'].replace('Z', '+00:00')) if data.get('season_start_time') else datetime.now()
        season_end_time = datetime.fromisoformat(data['season_end_time'].replace('Z', '+00:00')) if data.get('season_end_time') else datetime.now()
        
        new_tournament = Tournament(
            name=data['name'],
            season_name=data['season_name'],
            is_grouped=data.get('is_grouped', False),
            season_start_time=season_start_time,
            season_end_time=season_end_time
        )
        
        db.session.add(new_tournament)
        db.session.commit()
        
        return new_tournament
    
    @staticmethod
    def update_tournament(tournament_id: int, data: Dict[str, Any]) -> Tournament:
        """更新赛事信息"""
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            raise ValueError('赛事不存在')
        
        if data.get('name'):
            tournament.name = data['name']
        if data.get('season_name'):
            tournament.season_name = data['season_name']
        if 'is_grouped' in data:
            tournament.is_grouped = data['is_grouped']
        if data.get('season_start_time'):
            tournament.season_start_time = datetime.fromisoformat(data['season_start_time'].replace('Z', '+00:00'))
        if data.get('season_end_time'):
            tournament.season_end_time = datetime.fromisoformat(data['season_end_time'].replace('Z', '+00:00'))
        
        db.session.commit()
        return tournament
    
    @staticmethod
    def delete_tournament(tournament_id: int) -> None:
        """删除赛事"""
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            raise ValueError('赛事不存在')
        
        associated_teams = Team.query.filter_by(tournament_id=tournament_id).count()
        if associated_teams > 0:
            raise ValueError(f'无法删除，该赛事下还有 {associated_teams} 支球队')
        
        db.session.delete(tournament)
        db.session.commit()
    
    @staticmethod
    def create_tournament_instance(data: Dict[str, Any]) -> Tournament:
        """创建赛事实例"""
        competition = Competition.query.get(data['competition_id'])
        if not competition:
            raise ValueError('赛事不存在')
        
        season = Season.query.get(data['season_id'])
        if not season:
            raise ValueError('赛季不存在')
        
        existing_tournament = Tournament.query.filter_by(
            competition_id=data['competition_id'],
            season_id=data['season_id']
        ).first()
        
        if existing_tournament:
            raise ValueError('该赛事和赛季的组合已存在')
        
        tournament = Tournament(
            competition_id=data['competition_id'],
            season_id=data['season_id'],
            is_grouped=data.get('is_grouped', False),
            group_count=data.get('group_count'),
            playoff_spots=data.get('playoff_spots')
        )
        
        db.session.add(tournament)
        db.session.commit()
        
        return tournament
    
    @staticmethod
    def update_tournament_instance(tournament_id: int, data: Dict[str, Any]) -> Tournament:
        """更新赛事实例"""
        tournament = Tournament.query.get(tournament_id)
        if not tournament:
            raise ValueError('赛事不存在')
        
        if 'competition_id' in data:
            competition = Competition.query.get(data['competition_id'])
            if not competition:
                raise ValueError('赛事不存在')
            tournament.competition_id = data['competition_id']
        
        if 'season_id' in data:
            season = Season.query.get(data['season_id'])
            if not season:
                raise ValueError('赛季不存在')
            tournament.season_id = data['season_id']
        
        if 'is_grouped' in data:
            tournament.is_grouped = data['is_grouped']
        
        if 'group_count' in data:
            tournament.group_count = data['group_count']
        
        if 'playoff_spots' in data:
            tournament.playoff_spots = data['playoff_spots']
        
        db.session.commit()
        return tournament

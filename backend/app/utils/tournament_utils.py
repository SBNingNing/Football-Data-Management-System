"""
赛事工具层
提供赛事相关的工具函数和数据处理功能
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import urllib.parse

from app.models.tournament import Tournament


class TournamentUtils:
    """赛事工具类"""
    
    @staticmethod
    def decode_tournament_name(tournament_name: str) -> str:
        """解码赛事名称（处理URL编码）"""
        return urllib.parse.unquote(tournament_name, encoding='utf-8').strip()

    @staticmethod
    def determine_match_type(tournament: Optional[Tournament]) -> str:
        """从赛事对象推断 matchType (赛事名称)"""
        if tournament and tournament.competition:
            return tournament.competition.name
        if tournament:
            return tournament.name
        return '未知赛事'
    
    @staticmethod
    def safe_datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
        """安全地将datetime转换为ISO格式字符串"""
        if not dt:
            return None
        
        try:
            return dt.isoformat()
        except Exception:
            return str(dt)
    
    @staticmethod
    def parse_datetime_from_iso(iso_string: str) -> datetime:
        """从ISO格式字符串解析datetime"""
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    @staticmethod
    def build_tournament_dict_from_model(tournament: Tournament) -> Dict[str, Any]:
        """从Tournament模型构建字典"""
        tournament_dict = tournament.to_dict()
        tournament_dict['tournamentName'] = tournament_dict['name']
        tournament_dict.update({
            'teams': [],
            'teamCount': 0,
            'totalGoals': 0,
            'matches': [],
            'matchCount': 0,
            'seasonStartTime': tournament_dict['season_start_time'],
            'seasonEndTime': tournament_dict['season_end_time'],
            'isGrouped': tournament_dict['is_grouped'],
            'seasonName': tournament_dict['season_name']
        })
        
        return tournament_dict
    
    @staticmethod
    def calculate_tournament_statistics(teams_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算赛事统计数据"""
        total_goals = sum(team_data.get('goals', 0) for team_data in teams_data)
        total_red_cards = sum(team_data.get('redCards', 0) for team_data in teams_data)
        total_yellow_cards = sum(team_data.get('yellowCards', 0) for team_data in teams_data)
        total_players = sum(team_data.get('playerCount', 0) for team_data in teams_data)
        
        return {
            'totalGoals': total_goals,
            'totalRedCards': total_red_cards,
            'totalYellowCards': total_yellow_cards,
            'totalPlayers': total_players,
            'totalTeams': len(teams_data)
        }
    
    @staticmethod
    def format_player_data(player_history) -> Dict[str, Any]:
        """格式化球员数据"""
        return {
            'player_id': player_history.player_id,
            'player_name': player_history.player.name if hasattr(player_history, 'player') and player_history.player else f'球员{player_history.player_id}',
            'player_number': player_history.player_number,
            'goals': player_history.tournament_goals or 0,
            'redCards': player_history.tournament_red_cards or 0,
            'yellowCards': player_history.tournament_yellow_cards or 0,
            'remarks': player_history.remarks or ''
        }
    
    @staticmethod
    def format_team_data(team, players_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """格式化球队数据"""
        return {
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
    
    @staticmethod
    def validate_tournament_data(data: Dict[str, Any]) -> List[str]:
        """验证赛事数据"""
        errors = []
        
        if not data.get('name'):
            errors.append('赛事名称不能为空')
        
        if not data.get('season_name'):
            errors.append('赛季名称不能为空')
        
        # 验证时间格式
        if data.get('season_start_time'):
            try:
                TournamentUtils.parse_datetime_from_iso(data['season_start_time'])
            except ValueError:
                errors.append('赛季开始时间格式无效')
        
        if data.get('season_end_time'):
            try:
                TournamentUtils.parse_datetime_from_iso(data['season_end_time'])
            except ValueError:
                errors.append('赛季结束时间格式无效')
        
        return errors
    
    @staticmethod
    def sort_tournaments_by_name(tournaments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按名称排序赛事列表"""
        return sorted(tournaments, key=lambda x: x.get('name', ''))
    
    @staticmethod
    def filter_tournaments_by_season(tournaments: List[Dict[str, Any]], season_name: str) -> List[Dict[str, Any]]:
        """按赛季名称过滤赛事"""
        return [t for t in tournaments if t.get('seasonName', '').lower() == season_name.lower()]
    
    @staticmethod
    def get_tournament_name_variations(name: str) -> List[str]:
        """获取赛事名称的变体形式（用于模糊搜索）"""
        variations = [name]
        
        # 添加去除空格的版本
        variations.append(name.replace(' ', ''))
        
        # 添加小写版本
        variations.append(name.lower())
        
        # 添加大写版本
        variations.append(name.upper())
        
        return list(set(variations))  # 去重

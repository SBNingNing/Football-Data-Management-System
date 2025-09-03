"""
球员历史数据服务类
专门处理球员跨赛季查询和统计分析
"""

from app.models import Player, PlayerTeamHistory, Tournament, Season, Competition, TeamBase
from app import db
from sqlalchemy import desc, func
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional, Any


class PlayerHistoryService:
    """球员历史数据服务类"""
    
    @staticmethod
    def get_player_complete_history(player_id: str) -> Dict[str, Any]:
        """获取球员完整的跨赛季历史记录"""
        # 查找球员
        player = Player.query.get(player_id)
        if not player:
            raise ValueError(f'未找到球员: {player_id}')
        
        # 获取球员所有历史记录，按时间排序
        histories = PlayerTeamHistory.query.filter_by(
            player_id=player_id
        ).join(Tournament).join(Season).order_by(desc(Season.start_date)).all()
        
        if not histories:
            return {
                'player_info': PlayerHistoryService._get_player_basic_info(player),
                'seasons': [],
                'career_summary': PlayerHistoryService._get_empty_career_summary()
            }
        
        # 按赛季分组数据
        seasons_data = PlayerHistoryService._group_histories_by_season(histories)
        
        # 转换为列表格式并计算统计
        seasons_list = PlayerHistoryService._convert_seasons_to_list(seasons_data)
        
        # 计算职业生涯汇总
        career_summary = PlayerHistoryService._calculate_career_summary(histories)
        
        return {
            'player_info': PlayerHistoryService._get_player_basic_info(player),
            'seasons': seasons_list,
            'career_summary': career_summary
        }
    
    @staticmethod
    def get_player_season_performance(player_id: str, season_id: int) -> Dict[str, Any]:
        """获取球员在指定赛季的表现"""
        # 查找球员和赛季
        player = Player.query.get(player_id)
        if not player:
            raise ValueError(f'未找到球员: {player_id}')
        
        season = Season.query.get(season_id)
        if not season:
            raise ValueError(f'未找到赛季: {season_id}')
        
        # 获取该赛季的所有赛事
        tournaments = Tournament.query.filter_by(season_id=season_id).all()
        tournament_ids = [t.id for t in tournaments]
        
        # 获取球员在该赛季的所有记录
        histories = PlayerTeamHistory.query.filter(
            PlayerTeamHistory.player_id == player_id,
            PlayerTeamHistory.tournament_id.in_(tournament_ids)
        ).all()
        
        if not histories:
            return {
                'player_info': PlayerHistoryService._get_player_basic_info(player),
                'season_info': PlayerHistoryService._get_season_basic_info(season),
                'performance': [],
                'season_totals': PlayerHistoryService._get_empty_season_totals()
            }
        
        # 组织数据
        performance_data = []
        season_totals = PlayerHistoryService._calculate_season_totals(histories)
        
        for history in histories:
            performance_record = PlayerHistoryService._build_performance_record(history)
            performance_data.append(performance_record)
        
        return {
            'player_info': PlayerHistoryService._get_player_basic_info(player),
            'season_info': PlayerHistoryService._get_season_basic_info(season),
            'performance': performance_data,
            'season_totals': season_totals
        }
    
    @staticmethod
    def compare_players_across_seasons(player_ids: List[str], season_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """跨赛季球员对比"""
        comparison_data = []
        
        for player_id in player_ids:
            player = Player.query.get(player_id)
            if not player:
                continue
            
            # 构建查询条件
            query = PlayerTeamHistory.query.filter_by(player_id=player_id)
            
            if season_ids:
                # 如果指定了赛季，只查询这些赛季的数据
                tournaments = Tournament.query.filter(Tournament.season_id.in_(season_ids)).all()
                tournament_ids = [t.id for t in tournaments]
                query = query.filter(PlayerTeamHistory.tournament_id.in_(tournament_ids))
            
            histories = query.all()
            
            # 计算球员统计
            player_stats = PlayerHistoryService._calculate_career_summary(histories)
            player_stats['player_info'] = PlayerHistoryService._get_player_basic_info(player)
            
            comparison_data.append(player_stats)
        
        return {
            'comparison': comparison_data,
            'comparison_metadata': {
                'total_players': len(comparison_data),
                'season_filter': season_ids,
                'comparison_date': datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def get_player_team_changes(player_id: str) -> Dict[str, Any]:
        """获取球员转队历史"""
        player = Player.query.get(player_id)
        if not player:
            raise ValueError(f'未找到球员: {player_id}')
        
        # 获取球员所有历史记录，按时间排序
        histories = PlayerTeamHistory.query.filter_by(
            player_id=player_id
        ).join(Tournament).join(Season).order_by(Season.start_date, Tournament.id).all()
        
        if not histories:
            return {
                'player_info': PlayerHistoryService._get_player_basic_info(player),
                'team_changes': [],
                'summary': {'total_teams': 0, 'total_seasons': 0, 'total_tournaments': 0}
            }
        
        # 分析转队历史
        team_changes = []
        seen_teams = set()
        seasons_played = set()
        
        for history in histories:
            if not history.team or not history.tournament or not history.tournament.season:
                continue
            
            team_identifier = PlayerHistoryService._get_team_identifier(history.team)
            season_name = history.tournament.season.name
            
            team_record = PlayerHistoryService._build_team_change_record(history, team_identifier, seen_teams)
            
            team_changes.append(team_record)
            seen_teams.add(team_identifier)
            seasons_played.add(season_name)
        
        return {
            'player_info': PlayerHistoryService._get_player_basic_info(player),
            'team_changes': team_changes,
            'summary': {
                'total_teams': len(seen_teams),
                'total_seasons': len(seasons_played),
                'total_tournaments': len(team_changes)
            }
        }
    
    # 私有辅助方法
    
    @staticmethod
    def _get_player_basic_info(player: Player) -> Dict[str, Any]:
        """获取球员基础信息"""
        return {
            'id': player.id,
            'name': player.name,
            'career_goals': player.career_goals,
            'career_red_cards': player.career_red_cards,
            'career_yellow_cards': player.career_yellow_cards
        }
    
    @staticmethod
    def _get_season_basic_info(season: Season) -> Dict[str, Any]:
        """获取赛季基础信息"""
        return {
            'id': season.id,
            'name': season.name,
            'start_date': season.start_date.isoformat() if season.start_date else None,
            'end_date': season.end_date.isoformat() if season.end_date else None
        }
    
    @staticmethod
    def _group_histories_by_season(histories: List[PlayerTeamHistory]) -> Dict[str, Dict]:
        """按赛季分组历史记录"""
        seasons_data = defaultdict(lambda: {
            'season_info': {},
            'tournaments': defaultdict(lambda: {
                'tournament_info': {},
                'teams': []
            }),
            'season_totals': {
                'goals': 0,
                'yellow_cards': 0,
                'red_cards': 0,
                'teams_count': 0,
                'tournaments_count': 0
            }
        })
        
        for history in histories:
            if not history.tournament or not history.tournament.season:
                continue
                
            season = history.tournament.season
            tournament = history.tournament
            season_key = season.name
            tournament_key = tournament.name
            
            # 填充赛季信息
            if not seasons_data[season_key]['season_info']:
                seasons_data[season_key]['season_info'] = PlayerHistoryService._get_season_basic_info(season)
            
            # 填充赛事信息
            if not seasons_data[season_key]['tournaments'][tournament_key]['tournament_info']:
                seasons_data[season_key]['tournaments'][tournament_key]['tournament_info'] = {
                    'id': tournament.id,
                    'name': tournament.name,
                    'competition_name': tournament.competition.name if tournament.competition else None,
                }
            
            # 添加球队记录
            team_record = PlayerHistoryService._build_team_record(history)
            seasons_data[season_key]['tournaments'][tournament_key]['teams'].append(team_record)
            
            # 累加赛季统计
            seasons_data[season_key]['season_totals']['goals'] += history.tournament_goals
            seasons_data[season_key]['season_totals']['yellow_cards'] += history.tournament_yellow_cards
            seasons_data[season_key]['season_totals']['red_cards'] += history.tournament_red_cards
        
        return seasons_data
    
    @staticmethod
    def _build_team_record(history: PlayerTeamHistory) -> Dict[str, Any]:
        """构建球队记录"""
        return {
            'team_id': history.team_id,
            'team_name': history.team.name if history.team else None,
            'team_base_name': history.team.team_base.name if history.team and history.team.team_base else None,
            'player_number': history.player_number,
            'goals': history.tournament_goals,
            'yellow_cards': history.tournament_yellow_cards,
            'red_cards': history.tournament_red_cards,
            'remarks': history.remarks
        }
    
    @staticmethod
    def _convert_seasons_to_list(seasons_data: Dict) -> List[Dict]:
        """将赛季数据转换为列表格式"""
        seasons_list = []
        
        for season_key in sorted(seasons_data.keys(), reverse=True):  # 按赛季倒序
            season_data = seasons_data[season_key]
            
            tournaments_list = []
            unique_teams = set()
            
            for tournament_key, tournament_data in season_data['tournaments'].items():
                tournaments_list.append({
                    'tournament_info': tournament_data['tournament_info'],
                    'teams': tournament_data['teams']
                })
                
                # 统计不重复的球队
                for team_record in tournament_data['teams']:
                    team_identifier = team_record['team_base_name'] or team_record['team_name']
                    if team_identifier:
                        unique_teams.add(team_identifier)
            
            # 更新赛季统计
            season_data['season_totals']['teams_count'] = len(unique_teams)
            season_data['season_totals']['tournaments_count'] = len(tournaments_list)
            
            seasons_list.append({
                'season_info': season_data['season_info'],
                'tournaments': tournaments_list,
                'season_totals': season_data['season_totals']
            })
        
        return seasons_list
    
    @staticmethod
    def _calculate_career_summary(histories: List[PlayerTeamHistory]) -> Dict[str, Any]:
        """计算职业生涯汇总统计"""
        if not histories:
            return PlayerHistoryService._get_empty_career_summary()
        
        total_goals = sum(h.tournament_goals for h in histories)
        total_yellow_cards = sum(h.tournament_yellow_cards for h in histories)
        total_red_cards = sum(h.tournament_red_cards for h in histories)
        
        # 统计参与的赛季和赛事
        seasons = set()
        tournaments = set()
        teams = set()
        
        for history in histories:
            if history.tournament and history.tournament.season:
                seasons.add(history.tournament.season.name)
                tournaments.add(history.tournament.name)
            
            if history.team:
                team_identifier = PlayerHistoryService._get_team_identifier(history.team)
                teams.add(team_identifier)
        
        return {
            'total_goals': total_goals,
            'total_yellow_cards': total_yellow_cards,
            'total_red_cards': total_red_cards,
            'seasons_played': len(seasons),
            'tournaments_participated': len(tournaments),
            'teams_played_for': len(teams),
            'average_goals_per_tournament': round(total_goals / len(tournaments), 2) if tournaments else 0,
            'disciplinary_record': {
                'yellow_card_rate': round(total_yellow_cards / len(tournaments), 2) if tournaments else 0,
                'red_card_rate': round(total_red_cards / len(tournaments), 2) if tournaments else 0
            }
        }
    
    @staticmethod
    def _calculate_season_totals(histories: List[PlayerTeamHistory]) -> Dict[str, Any]:
        """计算赛季统计"""
        season_totals = {
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'tournaments_participated': 0,
            'teams_played_for': set()
        }
        
        for history in histories:
            season_totals['total_goals'] += history.tournament_goals
            season_totals['total_yellow_cards'] += history.tournament_yellow_cards
            season_totals['total_red_cards'] += history.tournament_red_cards
            season_totals['tournaments_participated'] += 1
            
            if history.team:
                team_identifier = PlayerHistoryService._get_team_identifier(history.team)
                season_totals['teams_played_for'].add(team_identifier)
        
        season_totals['teams_played_for'] = len(season_totals['teams_played_for'])
        return season_totals
    
    @staticmethod
    def _build_performance_record(history: PlayerTeamHistory) -> Dict[str, Any]:
        """构建表现记录"""
        tournament = history.tournament
        return {
            'tournament_id': tournament.id,
            'tournament_name': tournament.name,
            'competition_name': tournament.competition.name if tournament.competition else None,
            'team_id': history.team_id,
            'team_name': history.team.name if history.team else None,
            'team_base_name': history.team.team_base.name if history.team and history.team.team_base else None,
            'player_number': history.player_number,
            'goals': history.tournament_goals,
            'yellow_cards': history.tournament_yellow_cards,
            'red_cards': history.tournament_red_cards,
            'remarks': history.remarks
        }
    
    @staticmethod
    def _build_team_change_record(history: PlayerTeamHistory, team_identifier: str, seen_teams: set) -> Dict[str, Any]:
        """构建转队记录"""
        return {
            'season_name': history.tournament.season.name,
            'tournament_name': history.tournament.name,
            'competition_name': history.tournament.competition.name if history.tournament.competition else None,
            'team_name': team_identifier,
            'team_id': history.team_id,
            'player_number': history.player_number,
            'goals': history.tournament_goals,
            'yellow_cards': history.tournament_yellow_cards,
            'red_cards': history.tournament_red_cards,
            'is_new_team': team_identifier not in seen_teams
        }
    
    @staticmethod
    def _get_team_identifier(team) -> str:
        """获取球队标识符"""
        if team.team_base:
            return team.team_base.name
        else:
            return team.name
    
    @staticmethod
    def _get_empty_career_summary() -> Dict[str, Any]:
        """返回空的职业生涯汇总"""
        return {
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'seasons_played': 0,
            'tournaments_participated': 0,
            'teams_played_for': 0,
            'average_goals_per_tournament': 0,
            'disciplinary_record': {
                'yellow_card_rate': 0,
                'red_card_rate': 0
            }
        }
    
    @staticmethod
    def _get_empty_season_totals() -> Dict[str, Any]:
        """返回空的赛季统计"""
        return {
            'total_goals': 0,
            'total_yellow_cards': 0,
            'total_red_cards': 0,
            'tournaments_participated': 0,
            'teams_played_for': 0
        }

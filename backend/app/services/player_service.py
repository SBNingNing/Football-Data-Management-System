"""
球员服务层 - 处理球员相关的业务逻辑
"""
from app.database import db
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.models.tournament import Tournament
from app.utils.logger import get_logger
from typing import List, Dict, Any, Optional, Tuple
import traceback

logger = get_logger(__name__)


class PlayerService:
    """球员服务类"""

    @staticmethod
    def get_all_players() -> List[Dict[str, Any]]:
        """获取所有球员信息"""
        try:
            players = Player.query.all()
            players_data = []

            for player in players:
                try:
                    if not player or not hasattr(player, 'id') or not hasattr(player, 'name'):
                        logger.warning(f"跳过无效的球员对象: {player}")
                        continue
                    
                    player_dict = PlayerService._format_player_details(player)
                    players_data.append(player_dict)

                except Exception as player_error:
                    logger.error(f"处理球员 {getattr(player, 'id', 'unknown')} 时出错: {str(player_error)}", exc_info=True)
                    continue
            
            return players_data

        except Exception as e:
            logger.error(f"获取球员列表失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_player_by_id(player_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取单个球员信息"""
        try:
            player = Player.query.get(player_id)
            if not player:
                return None
            
            return PlayerService._format_player_details_with_seasons(player)

        except Exception as e:
            logger.error(f"获取球员 {player_id} 信息失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def create_player(player_data: Dict[str, Any]) -> Player:
        """创建球员"""
        player_id = player_data['studentId']
        
        existing_player = Player.query.get(player_id)
        if existing_player:
            raise ValueError('球员已存在')
        
        new_player = Player(
            id=player_id,
            name=player_data['name']
        )
        db.session.add(new_player)
        db.session.commit()
        logger.info(f"成功创建球员: ID={new_player.id}, 名称={new_player.name}")
        return new_player

    @staticmethod
    def update_player(player_id: str, update_data: Dict[str, Any]) -> Player:
        """更新球员信息"""
        player = Player.query.get(player_id)
        if not player:
            raise ValueError('球员不存在')
        
        if update_data.get('name'):
            player.name = update_data['name']
        
        db.session.commit()
        logger.info(f"成功更新球员: ID={player.id}")
        return player

    @staticmethod
    def delete_player(player_id: str):
        """删除球员"""
        player = Player.query.get(player_id)
        if not player:
            raise ValueError('球员不存在')
        
        # 删除关联的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(player_id=player_id).delete()
        
        db.session.delete(player)
        db.session.commit()
        logger.info(f"成功删除球员: ID={player_id}")

    @staticmethod
    def _format_player_details(player: Player) -> Dict[str, Any]:
        """格式化球员基本信息和所有队伍历史"""
        player_dict = player.to_dict()
        player_dict.setdefault('teamName', None)
        player_dict.setdefault('team_id', None)
        player_dict.setdefault('number', None)
        player_dict.setdefault('matchType', 'champions-cup')
        player_dict.setdefault('studentId', player.id)
        player_dict.setdefault('all_teams', [])

        try:
            all_histories = PlayerTeamHistory.query.filter_by(
                player_id=player.id
            ).order_by(PlayerTeamHistory.id.desc()).all()
            
            all_teams = []
            current_team_set = False
            
            for history in all_histories:
                if history and hasattr(history, 'team') and history.team:
                    team_info, match_type = PlayerService._get_history_team_info(history)
                    all_teams.append(team_info)
                    
                    if not current_team_set:
                        player_dict['teamName'] = history.team.name
                        player_dict['team_id'] = history.team_id
                        player_dict['number'] = history.player_number
                        player_dict['matchType'] = match_type
                        player_dict['tournament_name'] = team_info['tournament_name']
                        player_dict['season_name'] = team_info['season_name']
                        current_team_set = True
            
            player_dict['all_teams'] = all_teams
        except Exception as history_error:
            logger.error(f"获取球员 {player.id} 历史记录时出错: {str(history_error)}")
        
        return player_dict

    @staticmethod
    def _format_player_details_with_seasons(player: Player) -> Dict[str, Any]:
        """格式化球员详细信息，包含按赛季分组的数据"""
        player_dict = player.to_dict()
        player_dict.setdefault('team_histories', [])
        player_dict.setdefault('seasons', [])

        try:
            all_histories = PlayerTeamHistory.query.filter_by(player_id=player.id).all()
            team_histories = []
            seasons_data = {}

            for history in all_histories:
                if not history or not hasattr(history, 'team'):
                    continue
                
                team_info, match_type = PlayerService._get_history_team_info(history)
                team_histories.append(team_info)

                tournament = Tournament.query.get(history.tournament_id)
                if tournament and tournament.season_name:
                    season_key = tournament.season_name
                    if season_key not in seasons_data:
                        seasons_data[season_key] = {'season_name': season_key, 'tournaments': {}}
                    
                    if tournament.name not in seasons_data[season_key]['tournaments']:
                        seasons_data[season_key]['tournaments'][tournament.name] = {
                            'tournament_name': tournament.name,
                            'match_type': match_type,
                            'teams': []
                        }
                    
                    seasons_data[season_key]['tournaments'][tournament.name]['teams'].append({
                        'team_name': team_info['team_name'],
                        'team_id': team_info['team_id'],
                        'player_number': team_info['player_number'],
                        'tournament_goals': team_info['tournament_goals'],
                        'tournament_red_cards': team_info['tournament_red_cards'],
                        'tournament_yellow_cards': team_info['tournament_yellow_cards']
                    })

            # 计算赛季总统计数据
            for season_name, season_data in seasons_data.items():
                season_total_goals = 0
                season_total_yellow_cards = 0
                season_total_red_cards = 0
                for tournament_data in season_data['tournaments'].values():
                    for team_data in tournament_data['teams']:
                        season_total_goals += team_data['tournament_goals']
                        season_total_yellow_cards += team_data['tournament_yellow_cards']
                        season_total_red_cards += team_data['tournament_red_cards']
                
                seasons_data[season_name]['season_total_goals'] = season_total_goals
                seasons_data[season_name]['season_total_yellow_cards'] = season_total_yellow_cards
                seasons_data[season_name]['season_total_red_cards'] = season_total_red_cards

            player_dict['team_histories'] = team_histories
            player_dict['seasons'] = list(seasons_data.values())
        except Exception as e:
            logger.error(f"处理球员 {player.id} 详细历史记录时出错: {str(e)}")

        return player_dict

    @staticmethod
    def _get_history_team_info(history: PlayerTeamHistory) -> Tuple[Dict[str, Any], str]:
        """从历史记录中提取队伍信息和比赛类型"""
        tournament = Tournament.query.get(history.tournament_id) if history.tournament_id else None
        match_type = 'champions-cup'
        tournament_name = None
        season_name = None

        if tournament:
            tournament_name = tournament.name
            season_name = tournament.season_name
            name_lower = tournament.name.lower()
            if '冠军杯' in name_lower or 'champions' in name_lower:
                match_type = 'champions-cup'
            elif '巾帼杯' in name_lower or 'womens' in name_lower:
                match_type = 'womens-cup'
            elif '八人制' in name_lower or 'eight' in name_lower:
                match_type = 'eight-a-side'

        team_info = {
            'team_name': history.team.name,
            'team_id': history.team_id,
            'player_number': history.player_number,
            'tournament_id': history.tournament_id,
            'tournament_name': tournament_name,
            'season_name': season_name,
            'match_type': match_type,
            'tournament_goals': getattr(history, 'tournament_goals', 0),
            'tournament_yellow_cards': getattr(history, 'tournament_yellow_cards', 0),
            'tournament_red_cards': getattr(history, 'tournament_red_cards', 0)
        }
        return team_info, match_type

"""
事件服务层 - 处理事件相关的业务逻辑
"""
from app.database import db
from app.models.event import Event
from app.models.match import Match
from app.models.player import Player
from app.models.team import Team
from app.models.player_team_history import PlayerTeamHistory
from app.models.tournament import Tournament
from app.utils.logger import get_logger
from typing import Optional, List, Dict, Any

logger = get_logger(__name__)


class EventService:
    """事件服务类"""
    
    @staticmethod
    def create_event(event_data: Dict[str, Any]) -> Event:
        """创建事件"""
        try:
            # 查找比赛
            match = EventService._find_match(event_data['matchName'])
            if not match:
                raise ValueError(f'比赛不存在: {event_data["matchName"]}')
            
            # 查找球员
            player = Player.query.filter_by(name=event_data['playerName']).first()
            if not player:
                raise ValueError(f'球员不存在: {event_data["playerName"]}')
            
            # 获取主队和客队信息
            home_team = Team.query.get(match.home_team_id)
            away_team = Team.query.get(match.away_team_id)
            
            if not home_team or not away_team:
                raise ValueError('比赛队伍信息不完整')
            
            # 确定球员所属球队
            player_team_id = EventService._find_player_team(
                player.id, match.tournament_id, [home_team.id, away_team.id]
            )
            if not player_team_id:
                raise ValueError(f'球员 {event_data["playerName"]} 不属于该赛事的参赛队伍')
            
            # 创建事件
            new_event = Event(
                event_type=event_data['eventType'],
                match_id=match.id,
                team_id=player_team_id,
                player_id=player.id,
                event_time=int(event_data['eventTime'])
            )
            
            db.session.add(new_event)
            db.session.commit()
            
            logger.info(f"成功创建事件: ID={new_event.id}, 类型={event_data['eventType']}, "
                       f"球员={event_data['playerName']}, 时间={event_data['eventTime']}")
            
            return new_event
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建事件失败: {str(e)}")
            raise
    
    @staticmethod
    def get_all_events() -> List[Dict[str, Any]]:
        """获取所有事件"""
        try:
            events = Event.query.order_by(Event.id.desc()).all()
            events_data = []
            
            for event in events:
                try:
                    event_dict = EventService._format_event_data(event)
                    events_data.append(event_dict)
                except Exception as e:
                    logger.error(f"处理事件 {event.id} 时出错: {str(e)}")
                    # 添加基本事件信息，避免完全跳过
                    events_data.append(EventService._get_basic_event_data(event))
            
            return events_data
            
        except Exception as e:
            logger.error(f"获取事件列表失败: {str(e)}")
            raise
    
    @staticmethod
    def update_event(event_id: int, update_data: Dict[str, Any]) -> Event:
        """更新事件"""
        try:
            event = Event.query.get(event_id)
            if not event:
                raise ValueError('事件不存在')
            
            logger.info(f"更新事件 {event_id}, 原始数据: 类型={event.event_type}, "
                       f"时间={event.event_time}, 球员={event.player_id}")
            
            # 更新事件类型
            if update_data.get('eventType'):
                event.event_type = update_data['eventType']
                logger.info(f"更新事件类型为: {update_data['eventType']}")
            
            # 更新事件时间
            if update_data.get('eventTime') is not None:
                event.event_time = int(update_data['eventTime'])
                logger.info(f"更新事件时间为: {update_data['eventTime']}")
            
            # 更新球员
            if update_data.get('playerName'):
                player = Player.query.filter_by(name=update_data['playerName']).first()
                if not player:
                    raise ValueError(f'球员不存在: {update_data["playerName"]}')
                
                # 验证球员是否属于该比赛的球队
                match = Match.query.get(event.match_id)
                if not match:
                    raise ValueError('比赛信息异常')
                
                player_history = PlayerTeamHistory.query.filter_by(
                    player_id=player.id,
                    tournament_id=match.tournament_id
                ).first()
                
                if not player_history:
                    raise ValueError(f'球员 {update_data["playerName"]} 不属于该赛事')
                
                event.player_id = player.id
                event.team_id = player_history.team_id
                logger.info(f"更新球员为: {player.name} (ID: {player.id})")
            
            db.session.commit()
            logger.info(f"事件 {event_id} 更新成功")
            
            return event
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新事件 {event_id} 失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_event(event_id: int) -> bool:
        """删除事件"""
        try:
            event = Event.query.get(event_id)
            if not event:
                raise ValueError('事件不存在')
            
            logger.info(f"删除事件 {event_id}: 类型={event.event_type}, "
                       f"球员={event.player_id}, 时间={event.event_time}")
            
            db.session.delete(event)
            db.session.commit()
            
            logger.info(f"事件 {event_id} 删除成功")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除事件 {event_id} 失败: {str(e)}")
            raise
    
    @staticmethod
    def _find_match(match_name: str) -> Optional[Match]:
        """查找比赛的辅助函数"""
        try:
            logger.info(f"查找比赛: {match_name}")
            
            # 首先尝试根据比赛名称查找
            match = Match.query.filter_by(match_name=match_name).first()
            if match:
                logger.info(f"通过比赛名称找到比赛: {match.id}")
                return match
            
            # 如果没找到，尝试直接匹配比赛ID（如果传入的是ID格式）
            try:
                match_id = int(match_name)
                match = Match.query.filter_by(id=match_id).first()
                if match:
                    logger.info(f"通过ID找到比赛: {match.id}")
                    return match
            except (ValueError, TypeError):
                pass
            
            # 如果还没找到，尝试根据主队vs客队格式查找
            if 'vs' in match_name:
                try:
                    team_names = match_name.split(' vs ')
                    if len(team_names) == 2:
                        team1_name, team2_name = team_names[0].strip(), team_names[1].strip()
                        logger.info(f"尝试通过队伍名称查找: {team1_name} vs {team2_name}")
                        
                        # 查找所有比赛并检查队伍名称
                        matches = Match.query.all()
                        for m in matches:
                            try:
                                home_team = Team.query.get(m.home_team_id)
                                away_team = Team.query.get(m.away_team_id)
                                
                                if home_team and away_team:
                                    if ((home_team.name == team1_name and away_team.name == team2_name) or
                                        (home_team.name == team2_name and away_team.name == team1_name)):
                                        logger.info(f"通过队伍名称找到比赛: {m.id}")
                                        return m
                            except Exception as e:
                                logger.error(f"处理比赛 {m.id} 时出错: {str(e)}")
                                continue
                except Exception as e:
                    logger.error(f"解析队伍名称时出错: {str(e)}")
            
            logger.warning(f"未找到比赛: {match_name}")
            return None
            
        except Exception as e:
            logger.error(f"查找比赛时出错: {str(e)}")
            return None
    
    @staticmethod
    def _find_player_team(player_id: int, tournament_id: int, valid_team_ids: List[int]) -> Optional[int]:
        """查找球员在指定赛事中的队伍"""
        try:
            logger.info(f"查找球员队伍: player_id={player_id}, tournament_id={tournament_id}, "
                       f"valid_teams={valid_team_ids}")
            
            # 查找球员在该赛事中的队伍历史
            player_history = PlayerTeamHistory.query.filter_by(
                player_id=player_id,
                tournament_id=tournament_id
            ).first()
            
            if player_history:
                logger.info(f"找到球员队伍历史: team_id={player_history.team_id}")
                # 验证球员是否属于参赛队伍
                if player_history.team_id in valid_team_ids:
                    return player_history.team_id
                else:
                    logger.warning(f"球员队伍 {player_history.team_id} 不在参赛队伍中 {valid_team_ids}")
            else:
                logger.warning("未找到球员在该赛事中的队伍历史")
                
            return None
            
        except Exception as e:
            logger.error(f"查找球员队伍时出错: {str(e)}")
            return None
    
    @staticmethod
    def _format_event_data(event: Event) -> Dict[str, Any]:
        """格式化事件数据"""
        from app.utils.event_utils import determine_match_type
        
        event_dict = event.to_dict()
        
        # 分别查询关联数据
        match = Match.query.get(event.match_id)
        if match:
            # 优先使用比赛名称，如果没有则使用主队vs客队格式
            if match.match_name:
                event_dict['matchName'] = match.match_name
            else:
                home_team = Team.query.get(match.home_team_id)
                away_team = Team.query.get(match.away_team_id)
                
                if home_team and away_team:
                    event_dict['matchName'] = f"{home_team.name} vs {away_team.name}"
                else:
                    event_dict['matchName'] = '未知比赛'
            
            tournament = Tournament.query.get(match.tournament_id)
            event_dict['matchType'] = determine_match_type(tournament)
        else:
            event_dict['matchName'] = '未知比赛'
            event_dict['matchType'] = 'champions-cup'
        
        return event_dict
    
    @staticmethod
    def _get_basic_event_data(event: Event) -> Dict[str, Any]:
        """获取基本事件数据（用于异常情况）"""
        return {
            'id': event.id,
            'eventType': event.event_type,
            'matchId': event.match_id,
            'teamId': event.team_id,
            'playerId': event.player_id,
            'eventTime': event.event_time,
            'playerName': None,
            'teamName': None,
            'matchName': '数据异常',
            'matchType': 'champions-cup'
        }

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.event import Event
from app.models.match import Match
from app.models.player import Player
from app.models.team import Team
from app.models.player_team_history import PlayerTeamHistory
from app.models.tournament import Tournament
import logging

events_bp = Blueprint('events', __name__)

def determine_match_type(tournament):
    """根据赛事名称确定matchType"""
    if tournament:
        tournament_name = tournament.name.lower()
        if '冠军杯' in tournament_name or 'champions' in tournament_name:
            return 'champions-cup'
        elif '巾帼杯' in tournament_name or 'womens' in tournament_name:
            return 'womens-cup'
        elif '八人制' in tournament_name or 'eight' in tournament_name:
            return 'eight-a-side'
        else:
            return 'champions-cup'
    else:
        return 'champions-cup'

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """创建事件"""
    data = request.get_json()
    
    # 详细的请求数据验证
    if not data:
        return jsonify({'status': 'error', 'message': '请求数据为空'}), 401
    
    required_fields = ['matchName', 'eventType', 'playerName', 'eventTime']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return jsonify({'status': 'error', 'message': f'缺少必要信息: {missing_fields}'}), 402
    
    try:
        # 验证事件类型
        valid_event_types = ['进球', '乌龙球', '红牌', '黄牌']
        if data['eventType'] not in valid_event_types:
            return jsonify({'status': 'error', 'message': f'事件类型无效，支持的类型：{valid_event_types}'}), 403
        
        # 验证事件时间
        try:
            event_time_int = int(data['eventTime'])
            if event_time_int < 0 or event_time_int > 120:  # 允许加时赛
                return jsonify({'status': 'error', 'message': '事件时间无效(0-120分钟)'}), 404
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': '事件时间格式错误'}), 405
        
        # 根据比赛名称查找比赛
        match = None
        
        # 首先尝试根据比赛名称查找
        match = Match.query.filter_by(match_name=data['matchName']).first()
        
        # 如果没找到，尝试直接匹配比赛ID（如果传入的是ID格式）
        if not match:
            try:
                match = Match.query.filter_by(id=data['matchName']).first()
            except:
                pass
        
        # 如果还没找到，尝试根据主队vs客队格式查找
        if not match and 'vs' in data['matchName']:
            try:
                team_names = data['matchName'].split(' vs ')
                if len(team_names) == 2:
                    team1_name, team2_name = team_names[0].strip(), team_names[1].strip()
                    matches = Match.query.join(Team, Match.home_team_id == Team.id)\
                                       .join(Team, Match.away_team_id == Team.id, aliased=True)\
                                       .all()
                    for m in matches:
                        if ((m.home_team.name == team1_name and m.away_team.name == team2_name) or
                            (m.home_team.name == team2_name and m.away_team.name == team1_name)):
                            match = m
                            break
            except:
                pass
        
        if not match:
            return jsonify({'status': 'error', 'message': f'比赛不存在: {data["matchName"]}'}), 406
        
        # 查找球员
        player = Player.query.filter_by(name=data['playerName']).first()
        if not player:
            return jsonify({'status': 'error', 'message': f'球员不存在: {data["playerName"]}'}), 407
        
        # 获取主队和客队信息
        home_team = Team.query.get(match.home_team_id)
        away_team = Team.query.get(match.away_team_id)
        
        # 确定球员所属球队
        player_history = PlayerTeamHistory.query.filter_by(
            player_id=player.id,
            tournament_id=match.tournament_id
        ).first()
        
        if not player_history:
            return jsonify({'status': 'error', 'message': f'球员 {data["playerName"]} 不属于该赛事'}), 408
        
        # 验证球员是否属于参赛队伍
        if player_history.team_id not in [home_team.id, away_team.id]:
            return jsonify({'status': 'error', 'message': f'球员 {data["playerName"]} 不属于参赛队伍'}), 409
        
        # 创建事件（触发器会自动更新统计数据）
        new_event = Event(
            event_type=data['eventType'],
            match_id=match.id,
            team_id=player_history.team_id,
            player_id=player.id,
            event_time=event_time_int
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        logger.info(f"成功创建事件: 类型={data['eventType']}, 球员={data['playerName']}, 时间={event_time_int}")
        
        # 返回事件信息
        event_dict = new_event.to_dict()
        event_dict['matchName'] = data['matchName']
        
        tournament = Tournament.query.get(match.tournament_id)
        event_dict['matchType'] = determine_match_type(tournament)
        
        return jsonify({
            'status': 'success',
            'message': '事件创建成功，统计数据已自动更新',
            'data': event_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建事件失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@events_bp.route('', methods=['GET'])
@jwt_required()
def get_events():
    """获取所有事件"""
    try:
        # 简单查询，避免JOIN可能导致的问题
        events = Event.query.order_by(Event.id.desc()).all()
        events_data = []
        
        for event in events:
            try:
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
                
                events_data.append(event_dict)
                
            except Exception as e:
                logger.error(f"处理事件 {event.id} 时出错: {str(e)}")
                # 添加基本事件信息，避免完全跳过
                events_data.append({
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
                })
                continue
        
        return jsonify({'status': 'success', 'data': events_data}), 200
        
    except Exception as e:
        logger.error(f"获取事件列表失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """更新事件信息（触发器会自动处理统计数据）"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': '请求数据为空'}), 400
    
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'status': 'error', 'message': '事件不存在'}), 404
        
        # 记录原始数据用于调试
        logger.info(f"更新事件 {event_id}, 原始数据: 类型={event.event_type}, 时间={event.event_time}, 球员={event.player_id}")
        
        # 验证事件类型
        if data.get('eventType'):
            valid_event_types = ['进球', '乌龙球', '红牌', '黄牌']
            if data['eventType'] not in valid_event_types:
                return jsonify({'status': 'error', 'message': f'事件类型无效，支持的类型：{valid_event_types}'}), 400
            event.event_type = data['eventType']
            logger.info(f"更新事件类型为: {data['eventType']}")
        
        # 更新事件时间
        if data.get('eventTime') is not None:
            try:
                event_time_int = int(data['eventTime'])
                if event_time_int < 0 or event_time_int > 120:
                    return jsonify({'status': 'error', 'message': '事件时间无效(0-120分钟)'}), 400
                event.event_time = event_time_int
                logger.info(f"更新事件时间为: {event_time_int}")
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': '事件时间格式错误'}), 400
        
        # 更新球员
        if data.get('playerName'):
            player = Player.query.filter_by(name=data['playerName']).first()
            if player:
                # 验证球员是否属于该比赛的球队
                match = Match.query.get(event.match_id)
                if match:
                    player_history = PlayerTeamHistory.query.filter_by(
                        player_id=player.id,
                        tournament_id=match.tournament_id
                    ).first()
                    
                    if player_history:
                        event.player_id = player.id
                        event.team_id = player_history.team_id  # 同时更新球队ID
                        logger.info(f"更新球员为: {player.name} (ID: {player.id})")
                    else:
                        return jsonify({'status': 'error', 'message': f'球员 {data["playerName"]} 不属于该赛事'}), 400
                else:
                    return jsonify({'status': 'error', 'message': '比赛信息异常'}), 400
            else:
                return jsonify({'status': 'error', 'message': f'球员不存在: {data["playerName"]}'}), 400
        
        # 提交事务，触发器会自动处理统计数据
        db.session.commit()
        logger.info(f"事件 {event_id} 更新成功，触发器已自动调整统计数据")
        
        return jsonify({'status': 'success', 'message': '更新成功，统计数据已自动调整'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新事件 {event_id} 失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """删除事件（触发器会自动回滚统计数据）"""
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'status': 'error', 'message': '事件不存在'}), 404
        
        # 记录删除信息用于调试
        logger.info(f"删除事件 {event_id}: 类型={event.event_type}, 球员={event.player_id}, 时间={event.event_time}")
        
        db.session.delete(event)
        db.session.commit()
        
        logger.info(f"事件 {event_id} 删除成功，触发器已自动回滚统计数据")
        
        return jsonify({'status': 'success', 'message': '删除成功，统计数据已自动回滚'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除事件 {event_id} 失败: {str(e)}")
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
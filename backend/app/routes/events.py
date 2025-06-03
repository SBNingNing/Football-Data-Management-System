from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.event import Event
from app.models.match import Match
from app.models.player import Player
from app.models.team import Team
from app.models.player_team_history import PlayerTeamHistory

events_bp = Blueprint('events', __name__)

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """创建事件"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('matchName', 'eventType', 'playerName', 'eventTime')):
        return jsonify({'status': 'error', 'message': '缺少必要信息'}), 400
    
    try:
        # 根据比赛名称查找比赛
        match_teams = data['matchName'].split(' vs ')
        if len(match_teams) != 2:
            return jsonify({'status': 'error', 'message': '比赛名称格式错误'}), 400
        
        # 修复比赛查询逻辑
        home_team = Team.query.filter_by(name=match_teams[0].strip()).first()
        away_team = Team.query.filter_by(name=match_teams[1].strip()).first()
        
        if not home_team or not away_team:
            return jsonify({'status': 'error', 'message': '球队不存在'}), 400
        
        match = Match.query.filter(
            db.or_(
                db.and_(Match.home_team_id == home_team.id, Match.away_team_id == away_team.id),
                db.and_(Match.home_team_id == away_team.id, Match.away_team_id == home_team.id)
            )
        ).first()
        
        if not match:
            return jsonify({'status': 'error', 'message': '比赛不存在'}), 400
        
        # 查找球员
        player = Player.query.filter_by(name=data['playerName']).first()
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 400
        
        # 确定球员所属球队
        player_history = PlayerTeamHistory.query.filter_by(
            player_id=player.id,
            tournament_id=match.tournament_id
        ).first()
        
        if not player_history:
            return jsonify({'status': 'error', 'message': '球员不属于该赛事'}), 400
        
        # 创建事件
        new_event = Event(
            event_type=data['eventType'],
            match_id=match.id,
            team_id=player_history.team_id,
            player_id=player.id
        )
        db.session.add(new_event)
        db.session.commit()
        
        # 返回事件信息
        event_dict = new_event.to_dict()
        event_dict['matchName'] = data['matchName']
        event_dict['eventTime'] = data['eventTime']
        
        tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
        event_dict['matchType'] = tournament_to_match_type.get(match.tournament_id, 'champions-cup')
        
        return jsonify({
            'status': 'success',
            'message': '事件创建成功',
            'data': event_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@events_bp.route('', methods=['GET'])
@jwt_required()
def get_events():
    """获取所有事件"""
    try:
        events = Event.query.all()
        events_data = []
        
        for event in events:
            event_dict = event.to_dict()
            # 安全访问match属性
            if event.match:
                event_dict['matchName'] = f"{event.match.home_team.name} vs {event.match.away_team.name}"
                tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
                event_dict['matchType'] = tournament_to_match_type.get(event.match.tournament_id, 'champions-cup')
            else:
                event_dict['matchName'] = '未知比赛'
                event_dict['matchType'] = 'champions-cup'
            
            event_dict['eventTime'] = '90'  # 默认值，实际应从数据库获取
            events_data.append(event_dict)
        
        return jsonify({'status': 'success', 'data': events_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """更新事件信息"""
    data = request.get_json()
    
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'status': 'error', 'message': '事件不存在'}), 404
        
        # 更新事件信息
        if data.get('eventType'):
            event.event_type = data['eventType']
        
        if data.get('playerName'):
            player = Player.query.filter_by(name=data['playerName']).first()
            if player:
                event.player_id = player.id
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """删除事件"""
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'status': 'error', 'message': '事件不存在'}), 404
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

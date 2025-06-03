from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory

players_bp = Blueprint('players', __name__)

@players_bp.route('', methods=['GET'])
def get_players():
    """获取所有球员信息（公共接口）"""
    try:
        players = Player.query.all()
        players_data = []
        
        for player in players:
            player_dict = player.to_dict()
            
            # 获取球员当前的队伍信息
            current_history = PlayerTeamHistory.query.filter_by(player_id=player.id).first()
            if current_history:
                player_dict['team_name'] = current_history.team.name
                player_dict['team_id'] = current_history.team_id
                player_dict['player_number'] = current_history.player_number
                
                # 根据tournament_id确定matchType
                tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
                player_dict['matchType'] = tournament_to_match_type.get(current_history.tournament_id, 'champions-cup')
            else:
                player_dict['team_name'] = None
                player_dict['team_id'] = None
                player_dict['player_number'] = None
                player_dict['matchType'] = 'champions-cup'
            
            players_data.append(player_dict)
        
        return jsonify({'status': 'success', 'data': players_data}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

@players_bp.route('', methods=['POST'])
@jwt_required()
def create_player():
    """创建球员信息"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('studentId'):
        return jsonify({'status': 'error', 'message': '球员姓名和学号不能为空'}), 400
    
    try:
        player_id = data['studentId']
        
        # 检查球员是否已存在
        existing_player = Player.query.get(player_id)
        if existing_player:
            return jsonify({'status': 'error', 'message': '球员已存在'}), 400
        
        # 创建新球员
        new_player = Player(
            id=player_id,
            name=data['name']
        )
        db.session.add(new_player)
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': '球员创建成功',
            'data': new_player.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500

@players_bp.route('/<string:player_id>', methods=['PUT'])
@jwt_required()
def update_player(player_id):
    """更新球员信息"""
    data = request.get_json()
    
    try:
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        # 更新球员信息
        if data.get('name'):
            player.name = data['name']
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@players_bp.route('/<string:player_id>', methods=['DELETE'])
@jwt_required()
def delete_player(player_id):
    """删除球员"""
    try:
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        # 删除关联的球员-队伍历史记录
        PlayerTeamHistory.query.filter_by(player_id=player_id).delete()
        
        # 删除球员
        db.session.delete(player)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

@players_bp.route('/<string:player_id>', methods=['GET'])
def get_player(player_id):
    """获取单个球员信息"""
    try:
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        player_dict = player.to_dict()
        
        # 获取球员当前的队伍信息
        current_history = PlayerTeamHistory.query.filter_by(player_id=player.id).first()
        if current_history:
            player_dict['team_name'] = current_history.team.name
            player_dict['team_id'] = current_history.team_id
            player_dict['player_number'] = current_history.player_number
            
            # 根据tournament_id确定matchType
            tournament_to_match_type = {1: 'champions-cup', 2: 'womens-cup', 3: 'eight-a-side'}
            player_dict['matchType'] = tournament_to_match_type.get(current_history.tournament_id, 'champions-cup')
        else:
            player_dict['team_name'] = None
            player_dict['team_id'] = None
            player_dict['player_number'] = None
            player_dict['matchType'] = 'champions-cup'
        
        return jsonify({'status': 'success', 'data': player_dict}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

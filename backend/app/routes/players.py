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

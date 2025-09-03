from flask import Blueprint, request, jsonify
from app.services import PlayerHistoryService

player_history_bp = Blueprint('player_history', __name__)

@player_history_bp.route('/api/player-history/<player_id>/complete', methods=['GET'])
def get_player_complete_history(player_id):
    """获取球员完整的跨赛季历史记录"""
    try:
        result = PlayerHistoryService.get_player_complete_history(player_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@player_history_bp.route('/api/player-history/<player_id>/season/<int:season_id>', methods=['GET'])
def get_player_season_performance(player_id, season_id):
    """获取球员在指定赛季的表现"""
    try:
        result = PlayerHistoryService.get_player_season_performance(player_id, season_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@player_history_bp.route('/api/player-history/compare', methods=['POST'])
def compare_players_across_seasons():
    """跨赛季球员对比"""
    try:
        data = request.get_json()
        player_ids = data.get('player_ids', [])
        season_ids = data.get('season_ids', [])  # 可选：指定赛季范围
        
        if not player_ids:
            return jsonify({'error': '请提供要比较的球员ID'}), 400
        
        result = PlayerHistoryService.compare_players_across_seasons(player_ids, season_ids)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@player_history_bp.route('/api/player-history/team-changes/<player_id>', methods=['GET'])
def get_player_team_changes(player_id):
    """获取球员转队历史"""
    try:
        result = PlayerHistoryService.get_player_team_changes(player_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

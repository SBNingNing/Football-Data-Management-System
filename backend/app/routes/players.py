"""
球员路由层 - 专注于HTTP请求处理和响应
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.player_service import PlayerService
from app.middleware.player_middleware import validate_player_creation_data, validate_player_id
from app.utils.logger import get_logger

players_bp = Blueprint('players', __name__)
logger = get_logger(__name__)


@players_bp.route('', methods=['GET'])
def get_players():
    """获取所有球员信息（公共接口）"""
    try:
        players_data = PlayerService.get_all_players()
        return jsonify({
            'status': 'success', 
            'data': players_data,
            'total': len(players_data)
        }), 200
    except Exception as e:
        logger.error(f"获取球员列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': f'获取球员信息失败: {str(e)}',
            'data': []
        }), 500


@players_bp.route('/<string:player_id>', methods=['GET'])
@validate_player_id
def get_player(player_id):
    """获取单个球员信息"""
    try:
        player_data = PlayerService.get_player_by_id(player_id)
        if not player_data:
            return jsonify({'status': 'error', 'message': '球员不存在'}), 404
        
        return jsonify({'status': 'success', 'data': player_data}), 200
    except Exception as e:
        logger.error(f"获取球员 {player_id} 信息失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500


@players_bp.route('', methods=['POST'])
@jwt_required()
@validate_player_creation_data
def create_player():
    """创建球员信息"""
    try:
        data = request.get_json()
        new_player = PlayerService.create_player(data)
        return jsonify({
            'status': 'success', 
            'message': '球员创建成功',
            'data': new_player.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建球员失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'创建失败: {str(e)}'}), 500


@players_bp.route('/<string:player_id>', methods=['PUT'])
@jwt_required()
@validate_player_id
def update_player(player_id):
    """更新球员信息"""
    try:
        data = request.get_json()
        PlayerService.update_player(player_id, data)
        return jsonify({'status': 'success', 'message': '更新成功'}), 200
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"更新球员 {player_id} 失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@players_bp.route('/<string:player_id>', methods=['DELETE'])
@jwt_required()
@validate_player_id
def delete_player(player_id):
    """删除球员"""
    try:
        PlayerService.delete_player(player_id)
        return jsonify({'status': 'success', 'message': '删除成功'}), 200
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"删除球员 {player_id} 失败: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500
